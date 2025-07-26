import os, requests, uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Saga, SagaEvent, SagaState

SVC = {
    "CARTS"   : os.getenv("CARTS_URL",   "http://carts:8000"),
    "STOCKS"  : os.getenv("STOCKS_URL",  "http://stocks:8000"),
    "PRODUITS": os.getenv("PRODUITS_URL","http://produits:8000"),
}

class OrderSagaAPIView(APIView):
    def post(self, request):
        cart_id    = request.data["cart_id"]
        magasin_id = request.data["magasin_id"]

        saga = Saga.objects.create(cart_id=cart_id)
        saga.record(SagaEvent.Type.COMMANDE_CREEE, {"cart_id": str(cart_id), "magasin_id": str(magasin_id)})
        saga.state = SagaState.STARTED; saga.save()

        client_idem = request.headers.get("Idempotency-Key")
        idem_header = {"Idempotency-Key": client_idem or str(saga.id)}

        try:
            r = requests.post(f"{SVC['CARTS']}/api/caisse/{cart_id}/lock/",
                              headers=idem_header, timeout=5)
            if r.status_code == 409:
                g = requests.get(f"{SVC['CARTS']}/api/caisse/{cart_id}/", timeout=5)
                g.raise_for_status()
                lignes = g.json()["lines"]
            else:
                r.raise_for_status()
                lignes = r.json()["lines"]

            saga.state = SagaState.CART_LOCKED; saga.save()
            saga.record(SagaEvent.Type.PANIER_VERROUILLE, {"cart_id": str(cart_id)})

            # 2) Réservation de stock
            r = requests.post(f"{SVC['STOCKS']}/api/stock/reservations/",
                              json={"magasin_id": magasin_id, "lignes": lignes},
                              headers=idem_header, timeout=5)
            r.raise_for_status()
            saga.reservation_id = r.json()["id"]
            saga.state = SagaState.STOCK_RESERVED; saga.save()
            saga.record(SagaEvent.Type.STOCK_RESERVE, {"reservation_id": str(saga.reservation_id)})

            # 3) Vente
            lignes_vente = [
                {"produit_id": l["produit_id"], "quantite": l["quantite"], "prix_unit": l.get("prix_unit", "0.00")}
                for l in lignes
            ]
            r = requests.post(f"{SVC['PRODUITS']}/api/produits/ventes/",
                              json={"magasin_id": magasin_id, "lignes": lignes_vente},
                              headers=idem_header, timeout=5)
            r.raise_for_status()
            saga.vente_id = r.json()["id"]
            saga.state = SagaState.DONE; saga.save()
            saga.record(SagaEvent.Type.VENTE_CREEE, {"vente_id": saga.vente_id})
            saga.record(SagaEvent.Type.TERMINEE)

            return Response({"saga_id": str(saga.id), "vente_id": saga.vente_id}, status=201)

        except requests.RequestException as exc:
            saga.record(SagaEvent.Type.ECHEC, {"error": str(exc)})

            # release stock si une reservation existe
            if saga.reservation_id:
                try:
                    requests.delete(f"{SVC['STOCKS']}/api/stock/reservations/{saga.reservation_id}/",
                                    headers=idem_header, timeout=5)
                    saga.record(SagaEvent.Type.COMPENSATION, {"released_reservation": str(saga.reservation_id)})
                except Exception:
                    pass

            # unlock panier
            try:
                requests.post(f"{SVC['CARTS']}/api/caisse/{cart_id}/unlock/",
                              headers=idem_header, timeout=5)
                saga.record(SagaEvent.Type.COMPENSATION, {"unlocked_cart": str(cart_id)})
            except Exception:
                pass

            saga.state = SagaState.FAILED
            saga.last_error = str(exc)
            saga.save()
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
