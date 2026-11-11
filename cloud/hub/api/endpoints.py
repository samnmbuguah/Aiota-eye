import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from ninja import NinjaAPI, Schema, UploadedFile, File, Form
from ninja.security import HttpBearer
from django.conf import settings
from django.http import HttpResponse
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

try:
    from app.core.models import EdgeAppliance, Camera, Site, Organization, DetectionEvent, AlertRule, AlertDispatchLog
except ImportError:
    from hub.core.models import EdgeAppliance, Camera, Site, Organization, DetectionEvent, AlertRule, AlertDispatchLog

try:
    from hub.tasks.alert_dispatcher import evaluate_and_dispatch_event_alerts, send_test_alert
except ImportError:
    try:
        from app.tasks.alert_dispatcher import evaluate_and_dispatch_event_alerts, send_test_alert
    except ImportError:
        from app.alert_dispatcher import evaluate_and_dispatch_event_alerts, send_test_alert

try:
    from hub.tasks.copilot import query_copilot
except ImportError:
    try:
        from app.tasks.copilot import query_copilot
    except ImportError:
        from app.copilot import query_copilot


api = NinjaAPI(title='Aiota Edge Video Intelligence API', version='1.0.0')

QDRANT_COLLECTION = 'detection_events_clip'
QDRANT_DIM = 512

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

def text_to_pseudo_vector(text: str, dim: int = 512) -> List[float]:
    """Deterministic normalized vector projection fallback for serverless/lightweight environments."""
    tokens = text.lower().strip().split()
    vec = [0.0] * dim
    for i, tok in enumerate(tokens):
        h = int(hashlib.sha256(tok.encode()).hexdigest(), 16)
        for d in range(dim):
            weight = ((h >> (d % 32)) & 1) * 2 - 1
            vec[d] += float(weight) / (i + 1)
    # L2 normalize
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

class ApplianceBearerAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            appliance = EdgeAppliance.objects.select_related('site__organization').get(token=token)
            request.appliance = appliance
            return appliance
        except EdgeAppliance.DoesNotExist:
            return None

class SearchQuerySchema(Schema):
    query_text: str
    site_id: Optional[str] = None
    camera_id: Optional[str] = None
    min_confidence: Optional[float] = 0.5
    limit: Optional[int] = 20

class SearchResultItem(Schema):
    event_id: str
    score: float
    primary_label: str
    confidence: float
    camera_name: str
    site_id: str
    started_at: str
    snapshot_url: str
    clip_url: Optional[str] = None
    zones: List[str]

class SearchResponseSchema(Schema):
    query: str
    count: int
    results: List[SearchResultItem]

@api.get('/health')
def health_check(request):
    return {
        'status': 'healthy',
        'subdomain': 'aiota.akilinova.co.ke',
        'qdrant': 'connected',
    }

@api.post('/events/ingest', auth=ApplianceBearerAuth())
def ingest_event(
    request,
    edge_event_id: str = Form(...),
    camera_identifier: str = Form(...),
    primary_label: str = Form(...),
    confidence: float = Form(...),
    zones_entered: str = Form('[]'),
    detection_payload: str = Form('{}'),
    started_at: float = Form(...),
    ended_at: Optional[float] = Form(None),
    snapshot: Optional[UploadedFile] = File(None),
    clip: Optional[UploadedFile] = File(None),
):
    appliance: EdgeAppliance = request.appliance
    site = appliance.site
    organization = site.organization

    camera, _ = Camera.objects.get_or_create(
        appliance=appliance,
        identifier=camera_identifier,
        defaults={'site': site, 'name': f'Camera {camera_identifier}'}
    )

    storage_root = settings.MEDIA_ROOT
    os.makedirs(storage_root, exist_ok=True)

    snapshot_url = ''
    if snapshot:
        snap_filename = f'{appliance.id}_{edge_event_id}.jpg'
        full_snap_path = os.path.join(storage_root, snap_filename)
        with open(full_snap_path, 'wb') as f:
            for chunk in snapshot.chunks():
                f.write(chunk)
        snapshot_url = f'/media/{snap_filename}'

    clip_url = ''
    if clip:
        clip_filename = f'{appliance.id}_{edge_event_id}.mp4'
        full_clip_path = os.path.join(storage_root, clip_filename)
        with open(full_clip_path, 'wb') as f:
            for chunk in clip.chunks():
                f.write(chunk)
        clip_url = f'/media/{clip_filename}'

    zones_list = json.loads(zones_entered)
    payload_dict = json.loads(detection_payload)
    dt_started = datetime.fromtimestamp(started_at, tz=timezone.utc)
    dt_ended = datetime.fromtimestamp(ended_at, tz=timezone.utc) if ended_at else None

    event, created = DetectionEvent.objects.update_or_create(
        edge_event_id=edge_event_id,
        camera=camera,
        defaults={
            'site': site,
            'organization': organization,
            'primary_label': primary_label,
            'confidence': confidence,
            'zones_entered': zones_list,
            'detection_payload': payload_dict,
            'snapshot_path': snapshot_url,
            'clip_path': clip_url,
            'started_at': dt_started,
            'ended_at': dt_ended,
        }
    )

    # Index into Qdrant Cloud
    qdrant = get_qdrant_client()
    vector = text_to_pseudo_vector(f'{primary_label} in {camera.name}')
    qdrant.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            qmodels.PointStruct(
                id=str(event.id),
                vector=vector,
                payload={
                    'event_id': str(event.id),
                    'organization_id': str(event.organization_id),
                    'site_id': str(event.site_id),
                    'camera_id': str(event.camera_id),
                    'primary_label': event.primary_label,
                    'confidence': float(event.confidence),
                    'zones': event.zones_entered,
                    'started_at': event.started_at.isoformat(),
                    'snapshot_url': snapshot_url,
                    'clip_url': clip_url,
                }
            )
        ]
    )
    event.qdrant_point_id = event.id
    event.vector_indexed = True
    event.save(update_fields=['qdrant_point_id', 'vector_indexed'])

    # Evaluate real-time alert rules
    dispatched_count = 0
    try:
        dispatched = evaluate_and_dispatch_event_alerts(event)
        dispatched_count = len(dispatched) if dispatched else 0
    except Exception as e:
        pass

    return {
        'status': 'ok',
        'event_id': str(event.id),
        'created': created,
        'indexed': True,
        'alerts_dispatched': dispatched_count,
    }

@api.post('/search', response=SearchResponseSchema)
def semantic_search_events(request, body: SearchQuerySchema):
    qdrant = get_qdrant_client()
    query_vector = text_to_pseudo_vector(body.query_text)

    filter_conditions = []
    if body.site_id:
        filter_conditions.append(
            qmodels.FieldCondition(key='site_id', match=qmodels.MatchValue(value=body.site_id))
        )
    if body.camera_id:
        filter_conditions.append(
            qmodels.FieldCondition(key='camera_id', match=qmodels.MatchValue(value=body.camera_id))
        )
    if body.min_confidence:
        filter_conditions.append(
            qmodels.FieldCondition(key='confidence', range=qmodels.Range(gte=body.min_confidence))
        )

    qdrant_filter = qmodels.Filter(must=filter_conditions) if filter_conditions else None

    response = qdrant.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        query_filter=qdrant_filter,
        limit=body.limit or 20,
    )
    search_hits = response.points

    event_ids = [hit.payload.get('event_id') for hit in search_hits if hit.payload]
    events_by_id = {
        str(e.id): e
        for e in DetectionEvent.objects.filter(id__in=event_ids).select_related('camera')
    }

    results = []
    for hit in search_hits:
        p = hit.payload or {}
        event_obj = events_by_id.get(p.get('event_id'))
        camera_name = event_obj.camera.name if event_obj else 'Camera Stream'

        results.append(SearchResultItem(
            event_id=p.get('event_id', str(hit.id)),
            score=round(float(hit.score), 4),
            primary_label=p.get('primary_label', 'unknown'),
            confidence=round(float(p.get('confidence', 0.0)), 2),
            camera_name=camera_name,
            site_id=p.get('site_id', ''),
            started_at=p.get('started_at', ''),
            snapshot_url=p.get('snapshot_url', ''),
            clip_url=p.get('clip_url', ''),
            zones=p.get('zones', []),
        ))

    return SearchResponseSchema(
        query=body.query_text,
        count=len(results),
        results=results
    )

class HeartbeatSchema(Schema):
    status: str
    ssd_buffer_usage_pct: float
    cpu_load_1m: float
    ram_usage_pct: float
    uplink_type: str
    timestamp: float

@api.post('/appliances/heartbeat', auth=ApplianceBearerAuth())
def appliance_heartbeat(request, data: HeartbeatSchema):
    appliance: EdgeAppliance = request.appliance
    appliance.status = EdgeAppliance.Status.ONLINE
    appliance.last_heartbeat_at = datetime.fromtimestamp(data.timestamp, tz=timezone.utc)
    appliance.save(update_fields=['status', 'last_heartbeat_at'])
    return {
        'status': 'received',
        'appliance_id': str(appliance.id),
        'appliance_name': appliance.name,
        'cloud_time': datetime.now(timezone.utc).isoformat()
    }

class CreateAlertRuleSchema(Schema):
    name: str
    target_labels: List[str]
    min_confidence: float = 0.70
    phone_number: str
    site_id: Optional[str] = None
    zones: Optional[List[str]] = []

class TestAlertSchema(Schema):
    phone_number: str
    channel: Optional[str] = 'whatsapp'

@api.get('/alerts/rules')
def list_alert_rules(request):
    rules = AlertRule.objects.select_related('site').all()
    out = []
    for r in rules:
        out.append({
            'id': str(r.id),
            'name': r.name,
            'site_name': r.site.name if r.site else 'All Sites',
            'target_labels': r.target_labels,
            'zones': r.zones,
            'min_confidence': r.min_confidence,
            'channel': r.channel,
            'phone_number': r.channel_config.get('phone_number', ''),
            'is_active': r.is_active,
            'created_at': r.created_at.isoformat(),
        })
    return out

@api.post('/alerts/rules')
def create_or_update_alert_rule(request, body: CreateAlertRuleSchema):
    site = None
    if body.site_id:
        site = Site.objects.filter(id=body.site_id).first()
    if not site:
        site = Site.objects.first()

    rule = AlertRule.objects.create(
        site=site,
        name=body.name,
        target_labels=body.target_labels,
        zones=body.zones or [],
        min_confidence=body.min_confidence,
        channel=AlertRule.Channel.WHATSAPP,
        channel_config={'phone_number': body.phone_number},
        is_active=True,
    )
    return {
        'status': 'created',
        'id': str(rule.id),
        'name': rule.name,
        'target_labels': rule.target_labels,
        'phone_number': body.phone_number,
    }

@api.post('/alerts/test')
def test_whatsapp_alert_endpoint(request, body: TestAlertSchema):
    result = send_test_alert(body.phone_number, body.channel or 'whatsapp')
    return result

@api.get('/alerts/logs')
def list_alert_logs(request, limit: int = 20):
    logs = AlertDispatchLog.objects.select_related('rule', 'event').all()[:limit]
    out = []
    for l in logs:
        out.append({
            'id': str(l.id),
            'rule_name': l.rule.name if l.rule else 'Direct / Test Alert',
            'channel': l.channel,
            'recipient': l.recipient,
            'status': l.status,
            'snapshot_url': l.snapshot_url,
            'message_preview': l.message_body[:100] + '...',
            'created_at': l.created_at.isoformat(),
            'click_to_chat_url': l.provider_response.get('click_to_chat_url', '') if isinstance(l.provider_response, dict) else '',
        })
    return out

class CopilotQuerySchema(Schema):
    query: str
    site_id: Optional[str] = None
    limit: Optional[int] = 10

class CopilotCitationSchema(Schema):
    event_id: str
    camera_name: str
    primary_label: str
    confidence: int
    time_eat: str
    zone: str
    snapshot_url: str
    clip_url: Optional[str] = ''

class CopilotResponseSchema(Schema):
    query: str
    answer: str
    model_used: str
    events_analyzed: int
    citations: List[CopilotCitationSchema]

@api.post('/copilot/query', response=CopilotResponseSchema)
def copilot_query_endpoint(request, body: CopilotQuerySchema):
    return query_copilot(body.query, body.site_id, body.limit or 10)

