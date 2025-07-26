# orchestrator/models.py
import uuid
from django.db import models

class Saga(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart_id = models.UUIDField()
    state = models.CharField(max_length=15, default="NEW")
    reservation_id = models.UUIDField(null=True, blank=True)
    payment_id = models.UUIDField(null=True, blank=True)
    order_id = models.UUIDField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
