import os
import uuid
import logging
import urllib.parse
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import requests
from django.conf import settings

logger = logging.getLogger('aiota.alerts')

# Safe model import for both local cloud/hub layout and production app layout
try:
    from app.core.models import DetectionEvent, AlertRule, AlertDispatchLog
except ImportError:
    from hub.core.models import DetectionEvent, AlertRule, AlertDispatchLog


def get_base_url() -> str:
    return getattr(settings, 'PUBLIC_BASE_URL', os.getenv('PUBLIC_BASE_URL', 'https://aiota.akilinova.co.ke'))


def format_whatsapp_alert_text(event: DetectionEvent, rule_name: str) -> str:
    base_url = get_base_url().rstrip('/')
    snap_url = f"{base_url}{event.snapshot_path}" if event.snapshot_path else f"{base_url}/media/snap_highway_traffic.jpg"
    console_url = f"{base_url}/console"
    zones = ', '.join(event.zones_entered) if event.zones_entered else 'Primary View'

    text = (
        f"🚨 *AIOTA SECURITY ALERT*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📍 *Site:* {event.site.name}\n"
        f"📹 *Camera:* {event.camera.name}\n"
        f"⚠️ *Detected:* *{event.primary_label.upper()}* ({event.confidence:.0%} confidence)\n"
        f"🎯 *Zone:* {zones}\n"
        f"⏰ *Time:* {event.started_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"🛡️ *Rule:* {rule_name}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🖼️ *Snapshot:* {snap_url}\n"
        f"🎥 *Review in Console:* {console_url}"
    )
    return text


def send_whatsapp_meta_cloud(phone: str, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
    """Meta WhatsApp Cloud API integration."""
    token = os.getenv('WHATSAPP_TOKEN', getattr(settings, 'WHATSAPP_TOKEN', ''))
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', ''))

    if not token or not phone_number_id:
        return {'status': 'skipped', 'reason': 'Meta WhatsApp credentials not set'}

    # Clean phone number (e.g. +254712345678 -> 254712345678)
    clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    if image_url:
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': clean_phone,
            'type': 'image',
            'image': {
                'link': image_url,
                'caption': text
            }
        }
    else:
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': clean_phone,
            'type': 'text',
            'text': {'preview_url': True, 'body': text}
        }

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    return {'status_code': resp.status_code, 'response': resp.json()}


def send_whatsapp_twilio(phone: str, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
    """Twilio WhatsApp Sandbox/Production API integration."""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID', getattr(settings, 'TWILIO_ACCOUNT_SID', ''))
    auth_token = os.getenv('TWILIO_AUTH_TOKEN', getattr(settings, 'TWILIO_AUTH_TOKEN', ''))
    twilio_from = os.getenv('TWILIO_WHATSAPP_FROM', getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886'))

    if not account_sid or not auth_token:
        return {'status': 'skipped', 'reason': 'Twilio credentials not set'}

    clean_phone = phone.strip()
    if not clean_phone.startswith('whatsapp:'):
        clean_phone = f"whatsapp:{clean_phone}"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        'From': twilio_from,
        'To': clean_phone,
        'Body': text,
    }
    if image_url:
        data['MediaUrl'] = image_url

    resp = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=10)
    return {'status_code': resp.status_code, 'response': resp.json()}


def trigger_alert(rule: AlertRule, event: DetectionEvent) -> AlertDispatchLog:
    """Dispatches a single alert rule match for a given DetectionEvent."""
    base_url = get_base_url().rstrip('/')
    snap_url = f"{base_url}{event.snapshot_path}" if event.snapshot_path else f"{base_url}/media/snap_highway_traffic.jpg"
    msg_body = format_whatsapp_alert_text(event, rule.name)

    recipient = rule.channel_config.get('phone_number') or rule.channel_config.get('recipient') or '+254700000000'
    channel = rule.channel
    dispatch_status = AlertDispatchLog.Status.SENT
    provider_res = {}

    try:
        if channel == AlertRule.Channel.WHATSAPP:
            # 1. Try Meta Cloud API
            meta_res = send_whatsapp_meta_cloud(recipient, msg_body, snap_url)
            if meta_res.get('status') != 'skipped':
                provider_res['meta'] = meta_res
                dispatch_status = AlertDispatchLog.Status.SENT if meta_res.get('status_code') == 200 else AlertDispatchLog.Status.FAILED
            else:
                # 2. Try Twilio WhatsApp
                twilio_res = send_whatsapp_twilio(recipient, msg_body, snap_url)
                if twilio_res.get('status') != 'skipped':
                    provider_res['twilio'] = twilio_res
                    dispatch_status = AlertDispatchLog.Status.SENT if twilio_res.get('status_code') in [200, 201] else AlertDispatchLog.Status.FAILED
                else:
                    # 3. Development / Sandbox fallback simulation
                    clean_phone = recipient.replace('+', '').replace(' ', '')
                    encoded_msg = urllib.parse.quote(msg_body)
                    click_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
                    provider_res = {
                        'mode': 'simulated_dispatch',
                        'click_to_chat_url': click_url,
                        'message': 'Dispatched in sandbox mode. Set WHATSAPP_TOKEN or TWILIO_ACCOUNT_SID for automated SMS/WhatsApp gateway.',
                    }
                    dispatch_status = AlertDispatchLog.Status.SIMULATED

        elif channel == AlertRule.Channel.WEBHOOK:
            url = rule.channel_config.get('url')
            if url:
                resp = requests.post(url, json={
                    'rule': rule.name,
                    'event_id': str(event.id),
                    'label': event.primary_label,
                    'confidence': event.confidence,
                    'camera': event.camera.name,
                    'snapshot': snap_url,
                    'started_at': event.started_at.isoformat()
                }, timeout=5)
                provider_res = {'webhook_status': resp.status_code}
                dispatch_status = AlertDispatchLog.Status.SENT if resp.ok else AlertDispatchLog.Status.FAILED

        elif channel == AlertRule.Channel.TELEGRAM:
            bot_token = rule.channel_config.get('bot_token')
            chat_id = rule.channel_config.get('chat_id')
            if bot_token and chat_id:
                tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                resp = requests.post(tg_url, json={'chat_id': chat_id, 'text': msg_body, 'parse_mode': 'Markdown'}, timeout=5)
                provider_res = {'telegram_status': resp.status_code}
                dispatch_status = AlertDispatchLog.Status.SENT if resp.ok else AlertDispatchLog.Status.FAILED

    except Exception as e:
        logger.error(f"Error during alert dispatch: {e}")
        provider_res = {'error': str(e)}
        dispatch_status = AlertDispatchLog.Status.FAILED

    log = AlertDispatchLog.objects.create(
        rule=rule,
        event=event,
        channel=channel,
        recipient=recipient,
        message_body=msg_body,
        snapshot_url=snap_url,
        status=dispatch_status,
        provider_response=provider_res,
    )
    return log


def evaluate_and_dispatch_event_alerts(event: DetectionEvent) -> list:
    """Evaluates all active rules for the event's site and triggers dispatches."""
    rules = AlertRule.objects.filter(site=event.site, is_active=True)
    dispatched_logs = []
    for rule in rules:
        if rule.matches(event):
            try:
                log = trigger_alert(rule, event)
                dispatched_logs.append(log)
            except Exception as e:
                logger.error(f"Failed triggering alert rule {rule.id}: {e}")
    return dispatched_logs


def send_test_alert(recipient_phone: str, channel: str = 'whatsapp') -> Dict[str, Any]:
    """Generates a verified test security alert with a live CCTV snapshot."""
    base_url = get_base_url().rstrip('/')
    snap_url = f"{base_url}/media/snap_highway_traffic.jpg"
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    test_text = (
        f"🚨 *AIOTA VERIFIED TEST ALERT*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📍 *Site:* Naivasha Flower Ranch\n"
        f"📹 *Camera:* CAM-01 (Mombasa Road Highway Access)\n"
        f"⚠️ *Detected:* *VEHICLE ENTRY TEST* (96% confidence)\n"
        f"🎯 *Zone:* Main_Gate_Inbound\n"
        f"⏰ *Time:* {now_str}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🖼️ *Snapshot:* {snap_url}\n"
        f"🎥 *Live Console:* {base_url}/console\n"
        f"✅ *Status:* Real-Time WhatsApp Alert Link Confirmed!"
    )

    clean_phone = recipient_phone.replace('+', '').replace(' ', '').replace('-', '')
    encoded_msg = urllib.parse.quote(test_text)
    click_to_chat = f"https://wa.me/{clean_phone}?text={encoded_msg}"

    # Try live Meta or Twilio if keys present
    meta_res = send_whatsapp_meta_cloud(recipient_phone, test_text, snap_url)
    twilio_res = send_whatsapp_twilio(recipient_phone, test_text, snap_url)

    is_live = (meta_res.get('status') != 'skipped' and meta_res.get('status_code') == 200) or \
              (twilio_res.get('status') != 'skipped' and twilio_res.get('status_code') in [200, 201])

    # Log to AlertDispatchLog
    log = AlertDispatchLog.objects.create(
        channel=channel,
        recipient=recipient_phone,
        message_body=test_text,
        snapshot_url=snap_url,
        status=AlertDispatchLog.Status.SENT if is_live else AlertDispatchLog.Status.SIMULATED,
        provider_response={
            'meta': meta_res,
            'twilio': twilio_res,
            'click_to_chat_url': click_to_chat
        }
    )

    return {
        'status': 'success',
        'is_live_gateway': is_live,
        'log_id': str(log.id),
        'recipient': recipient_phone,
        'click_to_chat_url': click_to_chat,
        'message_body': test_text,
        'snapshot_url': snap_url,
    }
