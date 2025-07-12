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

logger = logging.getLogger(__name__)

MONOLITHE_BASE_URL = 'http://web:8000/api/monolithe'

class StockMagasinAPIView(APIView):
    """API pour afficher le stock d'un magasin (proxy vers le monolithe)."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'stock_magasin.html'

    def get(self, request, magasin_id, response_format=None):
        base = MONOLITHE_BASE_URL
        # 1. Récupérer le magasin
        resp_mag = requests.get(f"{base}/magasins/{magasin_id}/")
        if resp_mag.status_code != 200:
            return Response({'error': 'Magasin introuvable'}, status=resp_mag.status_code)
        magasin = resp_mag.json()

        # 2. Récupérer tous les stocks puis filtrer pour ne garder que ceux du magasin_id
        resp_stocks = requests.get(f"{base}/stocks/", params={'magasin': magasin_id})
        if resp_stocks.status_code != 200:
            return Response({'error': 'Impossible de récupérer les stocks'}, status=resp_stocks.status_code)
        stocks = [
            s for s in resp_stocks.json()
            if s.get('magasin', {}).get('id') == magasin_id
        ]

        # 3. Récupérer les stocks du centre logistique
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
        # Récupérer le stock local
        resp_stock = requests.get(f"{base}/stocks/{stock_id}/")
        if resp_stock.status_code != 200:
            return Response({'error': 'Stock introuvable'}, status=resp_stock.status_code)
        stock = resp_stock.json()

        # Récupérer la quantité centrale pour ce produit
        resp_centre = requests.get(f"{base}/magasins/", params={'search': 'CENTRE_LOGISTIQUE'})
        central_qty = 0
        if resp_centre.status_code == 200 and resp_centre.json():
            centre_id = resp_centre.json()[0]['id']
            # Utiliser uniquement l'ID du produit
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
        # Vérifier le stock local
        resp_stock = requests.get(f"{base}/stocks/{stock_id}/")
        if resp_stock.status_code != 200:
            return Response({'error': 'Stock introuvable'}, status=resp_stock.status_code)
        stock = resp_stock.json()

        # Créer la demande via le monolithe (ID uniquement)
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