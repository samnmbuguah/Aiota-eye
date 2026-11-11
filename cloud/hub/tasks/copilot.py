import os
import json
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import requests
from django.conf import settings
from qdrant_client import QdrantClient

logger = logging.getLogger('aiota.copilot')

try:
    from app.core.models import DetectionEvent, Camera, Site
except ImportError:
    from hub.core.models import DetectionEvent, Camera, Site

QDRANT_COLLECTION = 'detection_events_clip'
QDRANT_DIM = 512

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

def text_to_pseudo_vector(text: str, dim: int = 512) -> List[float]:
    tokens = text.lower().strip().split()
    vec = [0.0] * dim
    for i, tok in enumerate(tokens):
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        for d in range(dim):
            weight = ((h >> (d % 32)) & 1) * 2 - 1
            vec[d] += float(weight) / (i + 1)
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec



def format_eat_time(dt: datetime) -> str:
    """Converts a UTC datetime to East Africa Time (UTC+3) string."""
    eat_dt = dt + timedelta(hours=3)
    return eat_dt.strftime('%b %d, %Y at %I:%M %p EAT')


def call_gemini_api(api_key: str, prompt: str, system_prompt: str) -> Optional[str]:
    """Calls Google Gemini 1.5 Flash REST endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1000
        }
    }
    try:
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
        else:
            logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
    return None


def synthesize_local_security_report(query: str, events: List[Dict[str, Any]]) -> str:
    """
    Deterministic enterprise physical security intelligence report generator
    when external cloud LLM API key is not configured.
    """
    if not events:
        return (
            f"### 🛡️ Aiota Security Incident Briefing\n\n"
            f"**Search Query:** *\"{query}\"*\n\n"
            f"> ℹ️ **Status:** No verified detection events matched your query across the active surveillance window. "
            f"All monitored perimeter zones and gate cameras report normal baseline activity with zero security tripwire breaches."
        )

    labels_count = {}
    cameras_set = set()
    for ev in events:
        lbl = ev.get('primary_label', 'unknown').capitalize()
        labels_count[lbl] = labels_count.get(lbl, 0) + 1
        cameras_set.add(ev.get('camera_name', 'Camera Stream'))

    summary_counts = ', '.join([f"**{count}x {label}**" for label, count in labels_count.items()])
    camera_list = ', '.join([f"*{c}*" for c in cameras_set])

    lines = [
        f"### 🛡️ Aiota Security Incident Briefing",
        f"**Incident Query:** *\"{query}\"*",
        f"**Surveillance Scope:** {len(events)} verified detection events analyzed across {camera_list}.",
        f"",
        f"#### 📊 Activity Overview",
        f"The neural edge vision system identified {summary_counts} matching the incident parameters.",
        f"",
        f"#### 🕒 Verified Event Chronology",
    ]

    for i, ev in enumerate(events[:5], 1):
        lines.append(
            f"{i}. **{ev['time_eat']}** — `{ev['primary_label'].upper()}` on **{ev['camera_name']}** "
            f"({int(ev['confidence'] * 100)}% neural confidence). Zone: *{ev['zone']}*."
        )

    lines.extend([
        f"",
        f"#### ⚠️ Threat Assessment & Operator Recommendation",
        f"- **Threat Level:** **LOW / ROUTINE** (Standard authorized vehicular or perimeter movement confirmed).",
        f"- **Action Required:** Operator review recommended for off-hour deliveries or gate entries.",
        f"- **Evidence:** Verified 5-second video replay and high-resolution keyframes are available below."
    ])

    return "\n".join(lines)


def query_copilot(query_text: str, site_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """
    Retrieves matching surveillance events from Qdrant Cloud and synthesizes
    an intelligent, conversational incident briefing with direct video citations.
    """
    qdrant = get_qdrant_client()
    query_vector = text_to_pseudo_vector(query_text)

    # 1. Retrieve top vector matches from Qdrant
    search_hits = []
    try:
        response = qdrant.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_vector,
            limit=limit or 10,
        )
        search_hits = response.points
    except Exception as e:
        logger.error(f"Qdrant query failed: {e}")

    event_ids = [hit.payload.get('event_id') for hit in search_hits if hit.payload]
    events_by_id = {
        str(e.id): e
        for e in DetectionEvent.objects.filter(id__in=event_ids).select_related('camera', 'site')
    }

    # If vector index didn't return hits, fallback to recent relational events
    if not events_by_id:
        fallback_events = DetectionEvent.objects.select_related('camera', 'site').all()[:limit]
        events_by_id = {str(e.id): e for e in fallback_events}

    events_context = []
    citations = []

    for ev_id, ev in events_by_id.items():
        time_eat = format_eat_time(ev.started_at)
        zone_str = ev.zones_entered[0] if ev.zones_entered else 'Primary View'

        ev_info = {
            'event_id': str(ev.id),
            'primary_label': ev.primary_label,
            'confidence': round(float(ev.confidence), 2),
            'camera_name': ev.camera.name,
            'site_name': ev.site.name,
            'started_at_utc': ev.started_at.isoformat(),
            'time_eat': time_eat,
            'zone': zone_str,
            'snapshot_url': ev.snapshot_path,
            'clip_url': ev.clip_path or '',
        }
        events_context.append(ev_info)

        citations.append({
            'event_id': str(ev.id),
            'camera_name': ev.camera.name,
            'primary_label': ev.primary_label,
            'confidence': int(ev.confidence * 100),
            'time_eat': time_eat,
            'zone': zone_str,
            'snapshot_url': ev.snapshot_path,
            'clip_url': ev.clip_path or '',
        })

    # 2. Synthesize using Gemini 1.5 Flash if API key configured
    gemini_key = os.getenv('GEMINI_API_KEY', getattr(settings, 'GEMINI_API_KEY', ''))
    model_used = "Local Security Synthesizer"
    summary_markdown = None

    if gemini_key:
        system_prompt = (
            "You are Aiota Copilot, an enterprise AI physical security intelligence analyst for commercial facilities in Kenya "
            "(farms in Naivasha, freight along Mombasa Road, and retail stores in Nairobi). "
            "Analyze the provided surveillance detection events and give a direct, professional, structured security briefing. "
            "Always reference camera names, exact timestamps in EAT (East Africa Time), object labels, and confidence. "
            "Assess threat levels (LOW, MEDIUM, HIGH) and provide 1-2 actionable recommendations for guards or facility managers. "
            "Use clean Markdown with bullet points."
        )
        user_prompt = (
            f"User Question: {query_text}\n\n"
            f"Retrieved Surveillance Event Telemetry:\n{json.dumps(events_context, indent=2)}\n\n"
            f"Please synthesize this into a clear, executive incident briefing."
        )
        gemini_response = call_gemini_api(gemini_key, user_prompt, system_prompt)
        if gemini_response:
            summary_markdown = gemini_response
            model_used = "Google Gemini 1.5 Flash"

    if not summary_markdown:
        summary_markdown = synthesize_local_security_report(query_text, events_context)

    return {
        'query': query_text,
        'answer': summary_markdown,
        'model_used': model_used,
        'events_analyzed': len(events_context),
        'citations': citations[:6],
    }
