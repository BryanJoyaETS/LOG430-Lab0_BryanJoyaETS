# pylint: disable=no-member, import-error, too-few-public-methods
import logging
import requests
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from .serializers import ReservationCreateSerializer
from .models import Reservation, ReservationLine, Stock, ServiceEvent
from django.db import transaction


logger = logging.getLogger(__name__)

MONOLITHE_BASE_URL = 'http://web:8000/api/monolithe'

@method_decorator(cache_page(60 * 5), name='dispatch')
class StockMagasinAPIView(APIView):
    """API pour afficher le stock d'un magasin (proxy vers le monolithe)."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'stock_magasin.html'

    def get(self, request, magasin_id, response_format=None):
        base = MONOLITHE_BASE_URL
        resp_mag = requests.get(f"{base}/magasins/{magasin_id}/")
        if resp_mag.status_code != 200:
            return Response({'error': 'Magasin introuvable'}, status=resp_mag.status_code)
        magasin = resp_mag.json()

        resp_stocks = requests.get(f"{base}/stocks/", params={'magasin': magasin_id})
        if resp_stocks.status_code != 200:
            return Response({'error': 'Impossible de récupérer les stocks'}, status=resp_stocks.status_code)
        stocks = [
            s for s in resp_stocks.json()
            if s.get('magasin', {}).get('id') == magasin_id
        ]

        resp_centre = requests.get(f"{base}/magasins/", params={'search': 'CENTRE_LOGISTIQUE'})
        central_stocks = []
        if resp_centre.status_code == 200 and resp_centre.json():
            centre_id = resp_centre.json()[0]['id']
            resp_cstocks = requests.get(f"{base}/stocks/", params={'magasin': centre_id})
            if resp_cstocks.status_code == 200:
                central_stocks = resp_cstocks.json()

        payload = {
            'magasin': magasin,
            'stocks': stocks,
            'central_stocks': central_stocks,
        }
        if response_format == 'json' or request.accepted_renderer.format == 'json':
            return Response(payload)
        return Response(payload, template_name=self.template_name)


class ReapproAPIView(APIView):
    """API GET pour la page de réapprovisionnement (proxy vers le monolithe)."""
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'demande_reappro.html'

    def get(self, request, stock_id, response_format=None):
        base = MONOLITHE_BASE_URL
        resp_stock = requests.get(f"{base}/stocks/{stock_id}/")
        if resp_stock.status_code != 200:
            return Response({'error': 'Stock introuvable'}, status=resp_stock.status_code)
        stock = resp_stock.json()

        resp_centre = requests.get(f"{base}/magasins/", params={'search': 'CENTRE_LOGISTIQUE'})
        central_qty = 0
        if resp_centre.status_code == 200 and resp_centre.json():
            centre_id = resp_centre.json()[0]['id']
            produit_id = stock['produit']['id']
            resp_cstock = requests.get(
                f"{base}/stocks/",
                params={'magasin': centre_id, 'produit': produit_id}
            )
            if resp_cstock.status_code == 200 and resp_cstock.json():
                central_qty = resp_cstock.json()[0]['quantite']

        data = {
            'produit': stock['produit'],
            'magasin': stock['magasin'],
            'stock_local': stock['quantite'],
            'stock_central': central_qty,
        }
        if response_format == 'json' or request.accepted_renderer.format == 'json':
            return Response(data)
        return Response(data, template_name=self.template_name)


class DemandeReapproAPIView(APIView):
    """API POST pour enregistrer une demande de réapprovisionnement (proxy)."""
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'demande_reappro_utilisateur.html'

    def post(self, request, stock_id, response_format=None):
        base = MONOLITHE_BASE_URL
        resp_stock = requests.get(f"{base}/stocks/{stock_id}/")
        if resp_stock.status_code != 200:
            return Response({'error': 'Stock introuvable'}, status=resp_stock.status_code)
        stock = resp_stock.json()

        quantite = request.data.get('quantite')
        magasin_id = stock['magasin']['id']
        produit_id = stock['produit']['id']
        resp = requests.post(
            f"{base}/demandes/",
            json={
                'magasin': magasin_id,
                'produit': produit_id,
                'quantite': quantite
            }
        )
        if resp.status_code == status.HTTP_201_CREATED:
            return Response(resp.json(), template_name=self.template_name, status=status.HTTP_201_CREATED)
        return Response(resp.json(), status=resp.status_code)


class TraitementDemandeReapproAPIView(APIView):
    """API GET pour traiter les demandes (proxy pour liste pending)."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request, response_format=None):
        base = MONOLITHE_BASE_URL
        resp = requests.get(f"{base}/demandes/", params={'statut': 'pending'})
        if resp.status_code != 200:
            return Response({'error': 'Impossible de récupérer les demandes'}, status=resp.status_code)
        demandes = resp.json()
        context = {'demandes': demandes}
        return Response(context, template_name='traiter_demande_reappro.html')


class DemandeReapproActionAPIView(APIView):
    """API POST pour approuver/refuser une demande (proxy)."""
    def post(self, request, demande_id, response_format=None):
        base = MONOLITHE_BASE_URL
        action = request.data.get('action')
        resp = requests.post(
            f"{base}/demandes/{demande_id}/action/",
            json={'action': action}
        )
        return Response(resp.json(), status=resp.status_code)
    

_cache = {}

class CreateReservationAPIView(APIView):
    def post(self, request):
        corr = request.headers.get("Idempotency-Key", "")
        if corr and corr in _cache:
            return Response(_cache[corr], status=201)
        try:
            ser = ReservationCreateSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data

            with transaction.atomic():
                reserv = Reservation.objects.create(magasin_id=data["magasin_id"])
                for l in data["lignes"]:
                    stock = Stock.objects.select_for_update().get(
                        magasin_id=data["magasin_id"],
                        produit_id=l["produit_id"]
                    )
                    if stock.quantite < l["quantite"]:
                        raise ValueError("Stock insuffisant")
                    stock.quantite -= l["quantite"]
                    stock.save()
                    ReservationLine.objects.create(
                        reservation=reserv, produit_id=l["produit_id"], quantite=l["quantite"]
                    )

            resp = {"id": str(reserv.id)}
            if corr:
                _cache[corr] = resp
            log_event("CREATE_RESERVATION", ServiceEvent.Outcome.SUCCESS, corr, {"reservation_id": str(reserv.id)})
            return Response(resp, status=201)

        except Exception as e:
            log_event("CREATE_RESERVATION", ServiceEvent.Outcome.FAILURE, corr, {"error": str(e), "payload": request.data})
            raise

class DeleteReservationAPIView(APIView):
    def delete(self, request, reservation_id):
        corr = request.headers.get("Idempotency-Key", "") + "del"
        # idempotence simple :
        if corr in _cache:
            return Response(status=204)
        try:
            with transaction.atomic():
                reserv = Reservation.objects.select_for_update().get(id=reservation_id)
                if reserv.status != "RELEASED":
                    for line in reserv.lines.all():
                        stock = Stock.objects.select_for_update().get(
                            magasin=reserv.magasin, produit=line.produit
                        )
                        stock.quantite += line.quantite
                        stock.save()
                    reserv.status = "RELEASED"
                    reserv.save()
            _cache[corr] = True
            log_event("DELETE_RESERVATION", ServiceEvent.Outcome.SUCCESS, corr, {"reservation_id": str(reservation_id)})
            return Response(status=204)

        except Exception as e:
            log_event("DELETE_RESERVATION", ServiceEvent.Outcome.FAILURE, corr, {"reservation_id": str(reservation_id), "error": str(e)})
            raise

def log_event(action: str, outcome: str, correlation_id: str = "", detail: dict | None = None):
    ServiceEvent.objects.create(
        action=action,
        outcome=outcome,
        correlation_id=correlation_id or "",
        detail=detail or {},
    )
