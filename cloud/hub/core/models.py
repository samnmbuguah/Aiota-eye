import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """Top-level enterprise tenant boundary."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Site(models.Model):
    """
    Physical deployment boundary (Farm, Warehouse, Construction Site, Retail).
    Vertical tag is purely organizational; schemas remain domain-agnostic.
    """
    class VerticalType(models.TextChoices):
        AGRICULTURE = "agriculture", _("Agriculture / Remote Farming")
        CONSTRUCTION = "construction", _("Construction Site")
        LOGISTICS = "logistics", _("Logistics / Warehouse")
        RETAIL = "retail", _("Retail & Foot Traffic")
        GENERIC = "generic", _("Generic Surveillance")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="sites")
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    vertical = models.CharField(max_length=32, choices=VerticalType.choices, default=VerticalType.GENERIC)
    timezone = models.CharField(max_length=64, default="UTC")
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom site properties, GPS, zone definitions, dynamic tag sets",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "slug")

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class EdgeAppliance(models.Model):
    """Physical on-premise hardware node running Frigate and Edge Sync."""
    class Status(models.TextChoices):
        ONLINE = "online", _("Online")
        OFFLINE = "offline", _("Offline")
        DEGRADED = "degraded", _("Degraded")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="appliances")
    name = models.CharField(max_length=128)
    token = models.CharField(max_length=128, unique=True, help_text="Bearer auth token for edge sync")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    frigate_version = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OFFLINE)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.site.name} [{self.name}]"


class Camera(models.Model):
    """Camera channel configured on an Edge Appliance."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appliance = models.ForeignKey(EdgeAppliance, on_delete=models.CASCADE, related_name="cameras")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="cameras")
    name = models.CharField(max_length=128)
    identifier = models.CharField(max_length=64, help_text="Stream identifier matching Frigate config")
    rtsp_url_cached = models.CharField(max_length=512, blank=True)
    zones = models.JSONField(default=list, blank=True, help_text="Configured detection zones")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("appliance", "identifier")

    def __str__(self):
        return f"{self.site.name} - {self.name}"


class DetectionEvent(models.Model):
    """
    Indexed visual intelligence event.
    Stores metadata, media references, and vectors indexed into Qdrant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edge_event_id = models.CharField(max_length=64, db_index=True, help_text="Original Frigate event ID")
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="events")
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="events")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="events")

    primary_label = models.CharField(max_length=64, db_index=True)
    confidence = models.FloatField(db_index=True)
    zones_entered = models.JSONField(default=list, blank=True)
    
    # Fully dynamic detection payload: box coordinates, sub-labels, attributes
    detection_payload = models.JSONField(default=dict, blank=True)

    snapshot_path = models.CharField(max_length=512, help_text="Storage path or S3 key for image snapshot")
    clip_path = models.CharField(max_length=512, blank=True, null=True, help_text="Storage path or S3 key for event clip")

    qdrant_point_id = models.UUIDField(null=True, blank=True, db_index=True)
    vector_indexed = models.BooleanField(default=False, db_index=True)

    started_at = models.DateTimeField(db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["organization", "site", "-started_at"]),
            models.Index(fields=["primary_label", "-started_at"]),
        ]

    def __str__(self):
        return f"[{self.started_at}] {self.camera.name}: {self.primary_label} ({self.confidence:.2f})"


class AlertRule(models.Model):
    """Configurable domain-agnostic rule router for notifications."""
    class Channel(models.TextChoices):
        TELEGRAM = "telegram", _("Telegram")
        WEBHOOK = "webhook", _("Webhook")
        SMS = "sms", _("SMS")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="alert_rules")
    name = models.CharField(max_length=128)
    target_labels = models.JSONField(default=list, help_text="e.g. ['coyote', 'person', 'forklift']")
    zones = models.JSONField(default=list, blank=True, help_text="Trigger only within these zones")
    min_confidence = models.FloatField(default=0.70)
    channel = models.CharField(max_length=16, choices=Channel.choices)
    channel_config = models.JSONField(default=dict, help_text="Webhook URLs, Telegram Chat IDs, tokens")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def matches(self, event: DetectionEvent) -> bool:
        if not self.is_active:
            return False
        if event.confidence < self.min_confidence:
            return False
        if self.target_labels and event.primary_label not in self.target_labels:
            return False
        if self.zones and not set(self.zones).intersection(set(event.zones_entered)):
            return False
        return True
