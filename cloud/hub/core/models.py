import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class OrganizationMember(models.Model):
    class Role(models.TextChoices):
        OWNER = 'owner', _('Organization Owner')
        MANAGER = 'manager', _('Security Manager')
        OPERATOR = 'operator', _('Site Operator / Guard')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.OPERATOR)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.organization.name} ({self.role})'

class Site(models.Model):
    class VerticalType(models.TextChoices):
        AGRICULTURE = 'agriculture', _('Agriculture / Farming')
        CONSTRUCTION = 'construction', _('Construction Site')
        LOGISTICS = 'logistics', _('Logistics / Warehouse')
        RETAIL = 'retail', _('Commercial / Retail')
        GENERIC = 'generic', _('General Surveillance')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    vertical = models.CharField(max_length=32, choices=VerticalType.choices, default=VerticalType.GENERIC)
    timezone = models.CharField(max_length=64, default='Africa/Nairobi')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'slug')

    def __str__(self):
        return f'{self.organization.name} - {self.name}'

class EdgeAppliance(models.Model):
    class Status(models.TextChoices):
        ONLINE = 'online', _('Online')
        OFFLINE = 'offline', _('Offline')
        DEGRADED = 'degraded', _('Degraded')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='appliances')
    name = models.CharField(max_length=128)
    token = models.CharField(max_length=128, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    frigate_version = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OFFLINE)
    last_heartbeat_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.site.name} [{self.name}]'

class Camera(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appliance = models.ForeignKey(EdgeAppliance, on_delete=models.CASCADE, related_name='cameras')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='cameras')
    name = models.CharField(max_length=128)
    identifier = models.CharField(max_length=64)
    rtsp_url_cached = models.CharField(max_length=512, blank=True)
    demo_video_url = models.CharField(max_length=512, blank=True, help_text='Direct live video feed or HLS/MP4 loop for demo purposes')
    zones = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('appliance', 'identifier')

    def __str__(self):
        return f'{self.site.name} - {self.name}'

class DetectionEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edge_event_id = models.CharField(max_length=64, db_index=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='events')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='events')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='events')

    primary_label = models.CharField(max_length=64, db_index=True)
    confidence = models.FloatField(db_index=True)
    zones_entered = models.JSONField(default=list, blank=True)
    detection_payload = models.JSONField(default=dict, blank=True)

    snapshot_path = models.CharField(max_length=512)
    clip_path = models.CharField(max_length=512, blank=True, null=True)

    qdrant_point_id = models.UUIDField(null=True, blank=True, db_index=True)
    vector_indexed = models.BooleanField(default=False, db_index=True)

    started_at = models.DateTimeField(db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'[{self.started_at}] {self.camera.name}: {self.primary_label} ({self.confidence:.2f})'

class AlertRule(models.Model):
    class Channel(models.TextChoices):
        WHATSAPP = 'whatsapp', _('WhatsApp')
        TELEGRAM = 'telegram', _('Telegram')
        SMS = 'sms', _('SMS')
        WEBHOOK = 'webhook', _('Webhook')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='alert_rules')
    name = models.CharField(max_length=128)
    target_labels = models.JSONField(default=list)
    zones = models.JSONField(default=list, blank=True)
    min_confidence = models.FloatField(default=0.70)
    channel = models.CharField(max_length=16, choices=Channel.choices)
    channel_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def matches(self, event) -> bool:
        if not self.is_active:
            return False
        if event.confidence < self.min_confidence:
            return False
        if self.target_labels:
            labels_lower = [str(l).lower() for l in self.target_labels]
            if str(event.primary_label).lower() not in labels_lower:
                return False
        if self.zones and event.zones_entered:
            if not any(z in self.zones for z in event.zones_entered):
                return False
        return True

    def __str__(self):
        return f'{self.name} ({self.channel})'

class AlertDispatchLog(models.Model):
    class Status(models.TextChoices):
        SENT = 'sent', _('Sent')
        FAILED = 'failed', _('Failed')
        SIMULATED = 'simulated', _('Simulated')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(AlertRule, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    event = models.ForeignKey(DetectionEvent, on_delete=models.CASCADE, null=True, blank=True, related_name='alert_logs')
    channel = models.CharField(max_length=16, default='whatsapp')
    recipient = models.CharField(max_length=128)
    message_body = models.TextField()
    snapshot_url = models.CharField(max_length=512, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SENT)
    provider_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.channel} to {self.recipient} [{self.status}]'
