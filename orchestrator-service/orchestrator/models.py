# orchestrator/models.py
import uuid
from django.db import models
from django.db.models import Q  # NEW

class SagaState(models.TextChoices):
    NEW            = "NEW", "Nouvelle"
    STARTED        = "STARTED", "Démarrée"
    CART_LOCKED    = "CART_LOCKED", "Panier verrouillé"
    STOCK_RESERVED = "STOCK_RESERVED", "Stock réservé"
    DONE           = "DONE", "Terminée"
    FAILED         = "FAILED", "Échec"

class Saga(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart_id = models.UUIDField()
    state = models.CharField(max_length=20, choices=SagaState.choices, default=SagaState.NEW)
    reservation_id = models.UUIDField(null=True, blank=True)
    payment_id = models.UUIDField(null=True, blank=True)
    vente_id = models.IntegerField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    client_key = models.CharField(max_length=100, blank=True, db_index=True)
    response_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["client_key"],
                condition=~Q(client_key=""),
                name="uniq_client_key_not_empty",
            ),
        ]

    def record(self, etype: str, payload: dict | None = None):
        return SagaEvent.objects.create(saga=self, type=etype, payload=payload or {})

class SagaEvent(models.Model):
    class Type(models.TextChoices):
        COMMANDE_CREEE    = "COMMANDE_CREEE", "CommandeCréée"
        PANIER_VERROUILLE = "PANIER_VERROUILLE", "PanierVerrouillé"
        STOCK_RESERVE     = "STOCK_RESERVE", "StockRéservé"
        VENTE_CREEE       = "VENTE_CREEE", "VenteCréée"
        COMPENSATION      = "COMPENSATION", "Compensation"
        TERMINEE          = "TERMINEE", "Terminée"
        ECHEC             = "ECHEC", "Échec"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    saga = models.ForeignKey(Saga, on_delete=models.CASCADE, related_name="events")
    type = models.CharField(max_length=40, choices=Type.choices)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
