import os, requests, uuid, time, logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Saga, SagaEvent, SagaState
from .metrics import SAGA_STARTED, SAGA_COMPLETED, SAGA_FAILED, SAGA_STEP, SAGA_DURATION

log = logging.getLogger("saga")

SVC = {
    "CARTS"   : os.getenv("CARTS_URL",   "http://carts:8000"),
    "STOCKS"  : os.getenv("STOCKS_URL",  "http://stocks:8000"),
    "PRODUITS": os.getenv("PRODUITS_URL","http://produits:8000"),
}

IDEMP_HEADER = lambda saga_id: {
    "Idempotency-Key": str(saga_id),
    "X-Correlation-Id": str(saga_id), 
}

class OrderSagaAPIView(APIView):
    def post(self, request):
        scenario = "commande"
        t0 = time.monotonic()

        cart_id    = request.data["cart_id"]
        magasin_id = request.data["magasin_id"]
        saga       = Saga.objects.create(cart_id=cart_id)

        SagaEvent.objects.create(saga=saga, type="COMMANDE_CREEE",
                                 payload={"cart_id": cart_id, "magasin_id": str(magasin_id)})
        SAGA_STARTED.labels(scenario).inc()
        log.info("saga_event", extra={"saga_id": str(saga.id), "event":"COMMANDE_CREEE",
                                      "state": saga.state, "cart_id": cart_id})

        try:
            # 1) LOCK
            r = requests.post(f"{SVC['CARTS']}/api/caisse/{cart_id}/lock/",
                              headers=IDEMP_HEADER(saga.id), timeout=5)
            r.raise_for_status()
            lignes = r.json()["lines"]
            saga.state = "CART_LOCKED"; saga.save()
            SagaEvent.objects.create(saga=saga, type="PANIER_VERROUILLE", payload={"cart_id": cart_id})
            SAGA_STEP.labels(scenario, "CART_LOCKED").inc()
            log.info("saga_event", extra={"saga_id":str(saga.id),"event":"PANIER_VERROUILLE","state":saga.state})

            # 2) RÉSERVATION
            r = requests.post(f"{SVC['STOCKS']}/api/stock/reservations/",
                              json={"magasin_id": magasin_id, "lignes": lignes},
                              headers=IDEMP_HEADER(saga.id), timeout=5)
            r.raise_for_status()
            saga.reservation_id = r.json()["id"]
            saga.state = "STOCK_RESERVED"; saga.save()
            SagaEvent.objects.create(saga=saga, type="STOCK_RESERVE",
                                     payload={"reservation_id": saga.reservation_id})
            SAGA_STEP.labels(scenario, "STOCK_RESERVED").inc()
            log.info("saga_event", extra={"saga_id":str(saga.id),"event":"STOCK_RESERVE","state":saga.state})

            # 3) VENTE
            lignes_vente = [{"produit_id": l["produit_id"], "quantite": l["quantite"],
                             "prix_unit": l.get("prix_unit", "0.00")} for l in lignes]
            r = requests.post(f"{SVC['PRODUITS']}/api/produits/ventes/",
                              json={"magasin_id": magasin_id, "lignes": lignes_vente},
                              headers=IDEMP_HEADER(saga.id), timeout=5)
            r.raise_for_status()
            saga.vente_id = r.json()["id"]
            saga.state = "DONE"; saga.save()
            SagaEvent.objects.create(saga=saga, type="VENTE_CREEE", payload={"vente_id": saga.vente_id})
            SagaEvent.objects.create(saga=saga, type="TERMINEE", payload={})
            SAGA_STEP.labels(scenario, "DONE").inc()
            SAGA_COMPLETED.labels(scenario).inc()
            SAGA_DURATION.observe(time.monotonic() - t0)

            log.info("saga_event", extra={"saga_id":str(saga.id),"event":"TERMINEE","state":saga.state})
            return Response({"saga_id": str(saga.id), "vente_id": saga.vente_id}, status=201)

        except requests.RequestException as exc:
            # compensations
            if saga.state == "STOCK_RESERVED":
                requests.delete(f"{SVC['STOCKS']}/api/stock/reservations/{saga.reservation_id}/",
                                headers=IDEMP_HEADER(saga.id), timeout=5)
            if saga.state in ("STOCK_RESERVED", "CART_LOCKED"):
                requests.post(f"{SVC['CARTS']}/api/caisse/{cart_id}/unlock/",
                              headers=IDEMP_HEADER(saga.id), timeout=5)

            saga.state = "FAILED"; saga.last_error = str(exc); saga.save()
            SagaEvent.objects.create(saga=saga, type="FAILED", payload={"error": str(exc)})
            SAGA_STEP.labels(scenario, "FAILED").inc()
            SAGA_FAILED.labels(scenario, saga.state).inc()
            SAGA_DURATION.observe(time.monotonic() - t0)
            log.error("saga_event", extra={"saga_id":str(saga.id),"event":"FAILED","state":saga.state,
                                           "error": str(exc)})
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
