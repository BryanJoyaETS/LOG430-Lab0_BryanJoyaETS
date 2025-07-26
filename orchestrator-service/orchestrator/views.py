# orchestrator/views.py
import os, requests, uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Saga

SVC = {
    "CARTS"   : os.getenv("CARTS_URL",   "http://carts:8000"),
    "STOCKS"  : os.getenv("STOCKS_URL",  "http://stocks:8000"),
    "PRODUITS": os.getenv("PRODUITS_URL","http://produits:8000"),
}

IDEMP_HEADER = lambda saga_id: {"Idempotency-Key": str(saga_id)}

class OrderSagaAPIView(APIView):
    """
    POST /api/commande/
    {
      "cart_id":   "<uuid>",
      "magasin_id":"<uuid>"
    }
    """
    def post(self, request):
        cart_id    = request.data["cart_id"]
        magasin_id = request.data["magasin_id"]
        saga       = Saga.objects.create(cart_id=cart_id)   # NEW

        try:
            # 1. Verrouiller le panier (LOCK) 
            r = requests.post(
                f"{SVC['CARTS']}/api/caisse/{cart_id}/lock/",
                headers=IDEMP_HEADER(saga.id), timeout=5
            )
            r.raise_for_status()
            lignes = r.json()["lines"]          
            saga.state = "CART_LOCKED"; saga.save()

            # 2. Réserver le stock
            r = requests.post(
                f"{SVC['STOCKS']}/api/stock/reservations/",
                json={"magasin_id": magasin_id, "lignes": lignes},
                headers=IDEMP_HEADER(saga.id), timeout=5
            )
            r.raise_for_status()
            saga.reservation_id = r.json()["id"]
            saga.state = "STOCK_RESERVED"; saga.save()

            # 3. Créer la vente
            lignes_vente = [
                {
                    "produit_id": l["produit_id"],
                    "quantite":   l["quantite"],
                    "prix_unit":  l.get("prix_unit", "0.00")
                }
                for l in lignes
            ]
            r = requests.post(
                f"{SVC['PRODUITS']}/api/produits/ventes/",
                json={"magasin_id": magasin_id, "lignes": lignes_vente},
                headers=IDEMP_HEADER(saga.id), timeout=5
            )
            r.raise_for_status()
            saga.vente_id = r.json()["id"]
            saga.state = "DONE"; saga.save()

            return Response({"vente_id": saga.vente_id}, status=201)

        except requests.RequestException as exc:
            # ---------- COMPENSATION ----------
            if saga.state == "STOCK_RESERVED":
                # libérer le stock
                requests.delete(
                    f"{SVC['STOCKS']}/api/stock/reservations/{saga.reservation_id}/",
                    headers=IDEMP_HEADER(saga.id), timeout=5
                )
            if saga.state in ("STOCK_RESERVED", "CART_LOCKED"):
                # déverrouiller le panier
                requests.post(
                    f"{SVC['CARTS']}/api/caisse/{cart_id}/unlock/",
                    headers=IDEMP_HEADER(saga.id), timeout=5
                )
            saga.state = "FAILED"
            saga.last_error = str(exc)
            saga.save()
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
