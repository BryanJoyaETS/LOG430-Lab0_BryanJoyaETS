# carts/views.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Magasin, Stock, Vente, LigneVente, Produit
from .serializers import (
    MagasinSerializer, StockSerializer, VenteSerializer, LigneVenteSerializer
)

from django.shortcuts import render, get_object_or_404
from .models import Magasin


# 1) CRUD sur Magasin, Stock, Vente
class MagasinViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer

class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.select_related('produit', 'magasin')
    serializer_class = StockSerializer

class VenteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Vente.objects.prefetch_related('lignes')
    serializer_class = VenteSerializer

# 2) Recherche de produit en stock (POST /api/caisse/{magasin_id}/recherche/)
class RechercheProduitAPIView(APIView):
    def post(self, request, magasin_id):
        filtres = {}
        if 'identifiant' in request.data:
            try:
                filtres['produit__id'] = int(request.data['identifiant'])
            except ValueError:
                return Response({'detail': 'ID invalide'}, status=400)
        if 'nom' in request.data:
            filtres['produit__nom__icontains'] = request.data['nom']
        if 'categorie' in request.data:
            filtres['produit__categorie__icontains'] = request.data['categorie']

        stocks = Stock.objects.filter(magasin_id=magasin_id, **filtres)\
                              .select_related('produit')
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)

# 3) Enregistrer une vente (POST /api/caisse/{magasin_id}/vente/)
class EnregistrerVenteAPIView(APIView):
    def post(self, request, magasin_id):
        prod_id = request.data.get('produit_id')
        qty     = request.data.get('quantite')
        # Validation rapide
        try:
            prod_id = int(prod_id); qty = int(qty)
            if qty < 1:
                raise ValueError()
        except (TypeError, ValueError):
            return Response({'detail': 'Données invalides'}, status=400)

        stock = get_object_or_404(Stock, magasin_id=magasin_id, produit_id=prod_id)
        if stock.quantite < qty:
            return Response({'detail': 'Stock insuffisant'}, status=409)

        # Transaction atomique
        with transaction.atomic():
            vente = Vente.objects.create(magasin_id=magasin_id)
            LigneVente.objects.create(
                vente=vente,
                produit_id=prod_id,
                quantite=qty,
                prix_unitaire=stock.produit.prix
            )
            stock.quantite -= qty
            stock.save()

        serializer = VenteSerializer(vente)
        return Response(serializer.data, status=201)

# 4) Traiter un retour (POST /api/caisse/{magasin_id}/retour/)
class TraiterRetourAPIView(APIView):
    def post(self, request, magasin_id):
        vid = request.data.get('vente_id')
        try:
            vid = int(vid)
        except (TypeError, ValueError):
            return Response({'detail': 'ID de vente invalide'}, status=400)

        vente = get_object_or_404(Vente, id=vid, magasin_id=magasin_id)
        with transaction.atomic():
            # remonte le stock
            for ligne in vente.lignes.all():
                stock, _ = Stock.objects.get_or_create(
                    magasin_id=magasin_id,
                    produit_id=ligne.produit_id,
                    defaults={'quantite': 0}
                )
                stock.quantite += ligne.quantite
                stock.save()
            vente.delete()

        return Response({'detail': f'Vente {vid} annulée'}, status=200)

# 5) Historique des ventes (GET /api/caisse/{magasin_id}/historique/)
class HistoriqueTransactionsAPIView(APIView):
    def get(self, request, magasin_id):
        ventes = Vente.objects.filter(magasin_id=magasin_id)\
                              .prefetch_related('lignes')\
                              .order_by('-date')
        serializer = VenteSerializer(ventes, many=True)
        return Response(serializer.data)

# carts/views.py
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView

from .models import Magasin

class InterfaceCaisseAPIView(APIView):
    """
    GET  /caisse/<magasin_id>/
    Affiche le menu HTML de la caisse pour ce magasin.
    """
    authentication_classes = []  # si tu veux pas d'auth
    permission_classes     = []

    def get(self, request, magasin_id):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        return render(request, 'carts/menu_caisse.html', {'magasin': magasin})

# FRONT HTML – servent les templates avec juste le contexte minimal
def interface_caisse(request, magasin_id):
    magasin = get_object_or_404(Magasin, id=magasin_id)
    return render(request, 'carts/menu_caisse.html', {'magasin': magasin})

def recherche_html(request, magasin_id):
    magasin = get_object_or_404(Magasin, id=magasin_id)
    return render(request, 'carts/recherche.html', {
        'magasin': magasin,
        # la recherche elle-même se fera en JS/appel API
    })

def vente_html(request, magasin_id):
    magasin = get_object_or_404(Magasin, id=magasin_id)
    return render(request, 'carts/vente.html', {'magasin': magasin})

def retour_html(request, magasin_id):
    magasin = get_object_or_404(Magasin, id=magasin_id)
    return render(request, 'carts/retour.html', {'magasin': magasin})

def historique_html(request, magasin_id):
    magasin = get_object_or_404(Magasin, id=magasin_id)
    return render(request, 'carts/historique.html', {'magasin': magasin})

def demande_reappro_html(request, stock_id):
    return render(request, 'carts/demande_reappro.html')

# carts/views.py

from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from .models import Magasin, Stock, DemandeReappro  # pense à définir ce modèle
from .serializers import DemandeReapproSerializer  # idem : un serializer pour DemandeReappro

class CartReapproAPIView(APIView):
    """
    GET  /api/reappro/<stock_id>/       → renvoie JSON { magasin, produit, stock_local, stock_central }
                                          ou le template HTML (demande_reappro.html)
    POST /api/reappro/<stock_id>/       → crée la DemandeReappro et renvoie JSON { message, magasin_id }
    """
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name   = 'carts/demande_reappro.html'

    def get(self, request, stock_id, response_format=None):
        stock = get_object_or_404(Stock, id=stock_id)

        try:
            centre  = Magasin.objects.get(nom="CENTRE_LOGISTIQUE")
            centr_stock = Stock.objects.get(magasin=centre, produit=stock.produit)
            central_qty  = centr_stock.quantite
        except (Magasin.DoesNotExist, Stock.DoesNotExist):
            central_qty = 0

        payload = {
            'magasin':     {'id': stock.magasin.id,  'nom': stock.magasin.nom},
            'produit':     {'id': stock.produit.id,  'nom': stock.produit.nom},
            'stock_local': stock.quantite,
            'stock_central': central_qty,
        }

        if response_format == 'html' or request.accepted_renderer.format == 'html':
            return Response(payload, template_name=self.template_name)

        return Response(payload)

    def post(self, request, stock_id, response_format=None):
        stock = get_object_or_404(Stock, id=stock_id)
        q = request.data.get('quantite')

        try:
            q = int(q)
            if q < 1:
                raise ValueError()
        except (TypeError, ValueError):
            return Response({'error': 'Quantité invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        demande = DemandeReappro.objects.create(
            magasin=stock.magasin,
            produit=stock.produit,
            quantite=q,
            statut='pending'
        )

        data = {
            'message':     'Demande de réapprovisionnement soumise avec succès.',
            'magasin_id':  stock.magasin.id
        }
        return Response(data, status=status.HTTP_201_CREATED, template_name=self.template_name)
