import os
import uuid
import torch
import open_clip
from PIL import Image
from io import BytesIO
from celery import shared_task
from django.conf import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from hub.core.models import DetectionEvent, AlertRule
import requests
import logging

logger = logging.getLogger(__name__)

# Lazy singleton model holder for Celery workers
_CLIP_MODEL = None
_CLIP_PREPROCESS = None
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

QDRANT_COLLECTION = "detection_events_clip"
QDRANT_DIM = 512


def get_clip_model():
    global _CLIP_MODEL, _CLIP_PREPROCESS
    if _CLIP_MODEL is None:
        logger.info(f"Loading OpenCLIP ViT-B-32 on {_DEVICE}...")
        _CLIP_MODEL, _, _CLIP_PREPROCESS = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="laion2b_s34b_b79k"
        )
        _CLIP_MODEL.to(_DEVICE)
        _CLIP_MODEL.eval()
    return _CLIP_MODEL, _CLIP_PREPROCESS


def get_qdrant_client() -> QdrantClient:
    url = getattr(settings, "QDRANT_URL", os.getenv("QDRANT_URL", "http://localhost:6333"))
    api_key = getattr(settings, "QDRANT_API_KEY", os.getenv("QDRANT_API_KEY", None))
    client = QdrantClient(url=url, api_key=api_key)
    
    # Ensure collection exists
    collections = [c.name for c in client.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=qmodels.VectorParams(
                size=QDRANT_DIM,
                distance=qmodels.Distance.COSINE
            ),
        )
    return client


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def process_event_embedding(self, event_id: str):
    """
    Downloads/loads event snapshot, generates OpenCLIP embedding vector,
    upserts into Qdrant vector database, and checks alert rules.
    """
    try:
        event = DetectionEvent.objects.select_related("camera", "site", "organization").get(id=event_id)
    except DetectionEvent.DoesNotExist:
        logger.error(f"DetectionEvent {event_id} not found.")
        return

    try:
        # Load snapshot image
        if os.path.exists(event.snapshot_path):
            image = Image.open(event.snapshot_path).convert("RGB")
        else:
            # Handle remote/S3/MinIO storage URL
            resp = requests.get(event.snapshot_path, timeout=10)
            resp.raise_for_status()
            image = Image.open(BytesIO(resp.content)).convert("RGB")

        # Compute CLIP Image Embedding
        model, preprocess = get_clip_model()
        image_tensor = preprocess(image).unsqueeze(0).to(_DEVICE)

        with torch.no_grad():
            image_features = model.encode_image(image_tensor)
            # L2 normalize
            image_features /= image_features.norm(dim=-1, keepdim=True)
            embedding_list = image_features.cpu().numpy()[0].tolist()

        # Upsert point into Qdrant with tenant payload filters
        point_id = str(event.id)
        qdrant = get_qdrant_client()
        
        payload = {
            "event_id": str(event.id),
            "organization_id": str(event.organization_id),
            "site_id": str(event.site_id),
            "camera_id": str(event.camera_id),
            "primary_label": event.primary_label,
            "confidence": float(event.confidence),
            "zones": event.zones_entered,
            "started_at": event.started_at.isoformat(),
            "snapshot_url": event.snapshot_path,
            "clip_url": event.clip_path or "",
        }

        qdrant.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=embedding_list,
                    payload=payload
                )
            ]
        )

        event.qdrant_point_id = uuid.UUID(point_id)
        event.vector_indexed = True
        event.save(update_fields=["qdrant_point_id", "vector_indexed"])
        logger.info(f"Indexed vector for event {event.id} ({event.primary_label}) in Qdrant")

        # Evaluate alert rules
        dispatch_alerts_for_event.delay(str(event.id))

    except Exception as exc:
        logger.error(f"Failed processing embedding for event {event_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task
def dispatch_alerts_for_event(event_id: str):
    """Evaluates tenant alert rules and notifies external webhooks/Telegram."""
    try:
        event = DetectionEvent.objects.select_related("site", "camera").get(id=event_id)
    except DetectionEvent.DoesNotExist:
        return

    rules = AlertRule.objects.filter(site=event.site, is_active=True)
    for rule in rules:
        if rule.matches(event):
            try:
                _trigger_channel(rule, event)
            except Exception as e:
                logger.error(f"Error triggering alert {rule.name} for event {event.id}: {e}")


def _trigger_channel(rule: AlertRule, event: DetectionEvent):
    logger.info(f"Dispatching alert [{rule.name}] via {rule.channel} for event {event.id}")
    msg = f"Alert: {event.primary_label.upper()} detected on {event.camera.name} ({event.confidence:.0%}) at {event.started_at}"

    if rule.channel == AlertRule.Channel.WEBHOOK:
        url = rule.channel_config.get("url")
        if url:
            requests.post(url, json={
                "alert_rule": rule.name,
                "event_id": str(event.id),
                "camera": event.camera.name,
                "label": event.primary_label,
                "confidence": event.confidence,
                "snapshot_url": event.snapshot_path,
                "clip_url": event.clip_path,
                "timestamp": event.started_at.isoformat()
            }, timeout=5)

    elif rule.channel == AlertRule.Channel.TELEGRAM:
        bot_token = rule.channel_config.get("bot_token")
        chat_id = rule.channel_config.get("chat_id")
        if bot_token and chat_id:
            tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            requests.post(tg_url, json={"chat_id": chat_id, "text": msg}, timeout=5)
