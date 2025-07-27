import os, requests, time, logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Saga, SagaEvent, SagaState
from .metrics import (
    SAGA_STARTED, SAGA_COMPLETED, SAGA_FAILED, SAGA_STEP, SAGA_DURATION
)

log = logging.getLogger("saga")

SVC = {
    "CARTS"   : os.getenv("CARTS_URL",   "http://carts:8000"),
    "STOCKS"  : os.getenv("STOCKS_URL",  "http://stocks:8000"),
    "PRODUITS": os.getenv("PRODUITS_URL","http://produits:8000"),
}

def IDEMP_HEADER(saga_id):
    return {"Idempotency-Key": str(saga_id), "X-Correlation-Id": str(saga_id)}

class OrderSagaAPIView(APIView):
    def post(self, request):
        scenario = "commande"
        t0 = time.monotonic()
        stage = "START"  

        cart_id    = request.data["cart_id"]
        magasin_id = request.data["magasin_id"]
        client_key = (request.headers.get("Idempotency-Key") or "").strip() 

        if client_key:
            prev = (Saga.objects
                    .filter(client_key=client_key)
                    .order_by("-created_at")
                    .first())
            if prev:
                if prev.state == SagaState.DONE:
                    payload = prev.response_payload or {
                        "saga_id": str(prev.id), "vente_id": prev.vente_id
                    }
                    return Response(payload, status=201)
                if prev.state == SagaState.FAILED:
                    return Response({"error": prev.last_error}, status=500)
                return Response({"saga_id": str(prev.id), "state": prev.state}, status=202)

        saga = Saga.objects.create(cart_id=cart_id, client_key=client_key)

        SagaEvent.objects.create(
            saga=saga, type=SagaEvent.Type.COMMANDE_CREEE,
            payload={"cart_id": str(cart_id), "magasin_id": str(magasin_id)}
        )
        SAGA_STARTED.labels(scenario).inc()
        log.info("saga_event", extra={"saga_id": str(saga.id),
                                      "event": "COMMANDE_CREEE",
                                      "state": saga.state,
                                      "cart_id": str(cart_id)})

        try:
            stage = "CART_LOCK"
            r = requests.post(
                f"{SVC['CARTS']}/api/caisse/{cart_id}/lock/",
                headers=IDEMP_HEADER(saga.id), timeout=5
            )
            r.raise_for_status()
            lignes = r.json()["lines"]
            saga.state = SagaState.CART_LOCKED; saga.save(update_fields=["state"])

            SagaEvent.objects.create(
                saga=saga, type=SagaEvent.Type.PANIER_VERROUILLE,
                payload={"cart_id": str(cart_id)}
            )
            SAGA_STEP.labels(scenario, "CART_LOCKED").inc()
            log.info("saga_event", extra={"saga_id": str(saga.id),
                                          "event": "PANIER_VERROUILLE",
                                          "state": saga.state})

            stage = "RESERVE"
            r = requests.post(
                f"{SVC['STOCKS']}/api/stock/reservations/",
                json={"magasin_id": magasin_id, "lignes": lignes},
                headers=IDEMP_HEADER(saga.id), timeout=5
            )
            r.raise_for_status()
            saga.reservation_id = r.json()["id"]
            saga.state = SagaState.STOCK_RESERVED
            saga.save(update_fields=["state", "reservation_id"])

            SagaEvent.objects.create(
                saga=saga, type=SagaEvent.Type.STOCK_RESERVE,
                payload={"reservation_id": str(saga.reservation_id)}
            )
            SAGA_STEP.labels(scenario, "STOCK_RESERVED").inc()
            log.info("saga_event", extra={"saga_id": str(saga.id),
                                          "event": "STOCK_RESERVE",
                                          "state": saga.state})

            stage = "VENTE"
            lignes_vente = [
                {
                    "produit_id": l["produit_id"],
                    "quantite":   l["quantite"],
                    "prix_unit":  l.get("prix_unit", "0.00"),
                } for l in lignes
            ]
            r = requests.post(
                f"{SVC['PRODUITS']}/api/produits/ventes/",
                json={"magasin_id": magasin_id, "lignes": lignes_vente},
                headers=IDEMP_HEADER(saga.id), timeout=5
            )
            r.raise_for_status()
            saga.vente_id = r.json()["id"]
            saga.state = SagaState.DONE
            payload = {"saga_id": str(saga.id), "vente_id": saga.vente_id}
            saga.response_payload = payload
            saga.save(update_fields=["state", "vente_id", "response_payload"])

            SagaEvent.objects.create(
                saga=saga, type=SagaEvent.Type.VENTE_CREEE,
                payload={"vente_id": saga.vente_id}
            )
            SagaEvent.objects.create(saga=saga, type=SagaEvent.Type.TERMINEE, payload={})
            SAGA_STEP.labels(scenario, "DONE").inc()
            SAGA_COMPLETED.labels(scenario).inc()
            SAGA_DURATION.observe(time.monotonic() - t0)

            log.info("saga_event", extra={"saga_id": str(saga.id),
                                          "event": "TERMINEE",
                                          "state": saga.state})
            return Response(payload, status=201)

        except requests.RequestException as exc:
            # --- COMPENSATIONS -------------------------------------------- #
            try:
                if saga.state == SagaState.STOCK_RESERVED and saga.reservation_id:
                    requests.delete(
                        f"{SVC['STOCKS']}/api/stock/reservations/{saga.reservation_id}/",
                        headers=IDEMP_HEADER(saga.id), timeout=5
                    )
                if saga.state in (SagaState.STOCK_RESERVED, SagaState.CART_LOCKED):
                    requests.post(
                        f"{SVC['CARTS']}/api/caisse/{cart_id}/unlock/",
                        headers=IDEMP_HEADER(saga.id), timeout=5
                    )
            finally:
                saga.state = SagaState.FAILED
                saga.last_error = str(exc)
                saga.save(update_fields=["state", "last_error"])

            SagaEvent.objects.create(
                saga=saga, type=SagaEvent.Type.ECHEC,
                payload={"error": str(exc), "stage": stage}
            )
            SAGA_STEP.labels(scenario, "FAILED").inc()
            SAGA_FAILED.labels(scenario, stage).inc()
            SAGA_DURATION.observe(time.monotonic() - t0)

            log.error("saga_event", extra={"saga_id": str(saga.id),
                                           "event": "ECHEC",
                                           "state": saga.state,
                                           "stage": stage,
                                           "error": str(exc)})
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
