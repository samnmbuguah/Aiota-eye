import os
import json
import torch
import open_clip
from datetime import datetime, timezone
from typing import List, Optional
from ninja import NinjaAPI, Schema, UploadedFile, File, Form
from ninja.security import HttpBearer
from django.conf import settings
from django.shortcuts import get_object_or_404
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from hub.core.models import EdgeAppliance, Camera, Site, DetectionEvent
from hub.tasks.vector_pipeline import (
    process_event_embedding,
    get_clip_model,
    get_qdrant_client,
    QDRANT_COLLECTION,
    _DEVICE
)

api = NinjaAPI(title="Aiota Edge Video Intelligence API", version="1.0.0")


class ApplianceBearerAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            appliance = EdgeAppliance.objects.select_related("site__organization").get(token=token)
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


@api.post("/events/ingest", auth=ApplianceBearerAuth())
def ingest_event(
    request,
    edge_event_id: str = Form(...),
    camera_identifier: str = Form(...),
    primary_label: str = Form(...),
    confidence: float = Form(...),
    zones_entered: str = Form("[]"),
    detection_payload: str = Form("{}"),
    started_at: float = Form(...),
    ended_at: Optional[float] = Form(None),
    snapshot: Optional[UploadedFile] = File(None),
    clip: Optional[UploadedFile] = File(None),
):
    """
    Ingestion endpoint invoked by EdgeSyncDaemon.
    Saves media artifacts, records event in PostgreSQL, and enqueues Celery vector task.
    """
    appliance: EdgeAppliance = request.appliance
    site = appliance.site
    organization = site.organization

    camera, _ = Camera.objects.get_or_create(
        appliance=appliance,
        identifier=camera_identifier,
        defaults={"site": site, "name": f"Camera {camera_identifier}"}
    )

    # Local media persistence folder (or integrate S3/MinIO in production)
    storage_root = getattr(settings, "MEDIA_ROOT", "/tmp/aiota_media")
    os.makedirs(storage_root, exist_ok=True)

    snapshot_path = ""
    if snapshot:
        snap_filename = f"{appliance.id}_{edge_event_id}.jpg"
        full_snap_path = os.path.join(storage_root, snap_filename)
        with open(full_snap_path, "wb") as f:
            for chunk in snapshot.chunks():
                f.write(chunk)
        snapshot_path = full_snap_path

    clip_path = None
    if clip:
        clip_filename = f"{appliance.id}_{edge_event_id}.mp4"
        full_clip_path = os.path.join(storage_root, clip_filename)
        with open(full_clip_path, "wb") as f:
            for chunk in clip.chunks():
                f.write(chunk)
        clip_path = full_clip_path

    zones_list = json.loads(zones_entered)
    payload_dict = json.loads(detection_payload)
    dt_started = datetime.fromtimestamp(started_at, tz=timezone.utc)
    dt_ended = datetime.fromtimestamp(ended_at, tz=timezone.utc) if ended_at else None

    # Upsert DetectionEvent
    event, created = DetectionEvent.objects.update_or_create(
        edge_event_id=edge_event_id,
        camera=camera,
        defaults={
            "site": site,
            "organization": organization,
            "primary_label": primary_label,
            "confidence": confidence,
            "zones_entered": zones_list,
            "detection_payload": payload_dict,
            "snapshot_path": snapshot_path,
            "clip_path": clip_path,
            "started_at": dt_started,
            "ended_at": dt_ended,
        }
    )

    # Trigger asynchronous OpenCLIP vector pipeline
    process_event_embedding.delay(str(event.id))

    return {
        "status": "ok",
        "event_id": str(event.id),
        "created": created,
        "indexed_async": True,
    }


@api.post("/search/", response=SearchResponseSchema)
def semantic_search_events(request, body: SearchQuerySchema):
    """
    Sub-second natural language visual search endpoint.
    Converts query text into CLIP text embedding, queries Qdrant with filters,
    and returns ranked event metadata.
    """
    model, _ = get_clip_model()
    qdrant = get_qdrant_client()

    # 1. Encode query text to 512-dim normalized vector
    text_tokens = open_clip.tokenize([body.query_text]).to(_DEVICE)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        query_vector = text_features.cpu().numpy()[0].tolist()

    # 2. Build Qdrant payload filters
    filter_conditions = []
    if body.site_id:
        filter_conditions.append(
            qmodels.FieldCondition(key="site_id", match=qmodels.MatchValue(value=body.site_id))
        )
    if body.camera_id:
        filter_conditions.append(
            qmodels.FieldCondition(key="camera_id", match=qmodels.MatchValue(value=body.camera_id))
        )
    if body.min_confidence:
        filter_conditions.append(
            qmodels.FieldCondition(key="confidence", range=qmodels.Range(gte=body.min_confidence))
        )

    qdrant_filter = qmodels.Filter(must=filter_conditions) if filter_conditions else None

    # 3. Perform Vector Similarity Search
    search_hits = qdrant.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        query_filter=qdrant_filter,
        limit=body.limit or 20,
        score_threshold=0.18,  # Minimum cosine similarity threshold
    )

    # 4. Resolve camera names from relational DB
    results = []
    event_ids = [hit.payload.get("event_id") for hit in search_hits if hit.payload]
    events_by_id = {
        str(e.id): e
        for e in DetectionEvent.objects.filter(id__in=event_ids).select_related("camera")
    }

    for hit in search_hits:
        p = hit.payload or {}
        event_obj = events_by_id.get(p.get("event_id"))
        camera_name = event_obj.camera.name if event_obj else "Unknown Camera"

        results.append(SearchResultItem(
            event_id=p.get("event_id", str(hit.id)),
            score=round(float(hit.score), 4),
            primary_label=p.get("primary_label", "unknown"),
            confidence=round(float(p.get("confidence", 0.0)), 2),
            camera_name=camera_name,
            site_id=p.get("site_id", ""),
            started_at=p.get("started_at", ""),
            snapshot_url=p.get("snapshot_url", ""),
            clip_url=p.get("clip_url", ""),
            zones=p.get("zones", []),
        ))

    return SearchResponseSchema(
        query=body.query_text,
        count=len(results),
        results=results
    )
