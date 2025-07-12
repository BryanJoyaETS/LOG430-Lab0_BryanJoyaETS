# application_multi_magasins/api_views.py
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from application_multi_magasins.models import (
    Magasin, Produit, Stock, Vente, LigneVente, DemandeReappro
)
from application_multi_magasins.serializers import (
    MagasinSerializer, ProduitSerializer, StockSerializer,
    VenteSerializer, LigneVenteSerializer, DemandeReapproSerializer
)

class ProduitViewSet(viewsets.ModelViewSet):
    """
    CRUD JSON pour les produits.
    """
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    renderer_classes = [JSONRenderer]

class MagasinViewSet(viewsets.ModelViewSet):
    """
    CRUD JSON pour les magasins.
    """
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer
    renderer_classes = [JSONRenderer]

class StockViewSet(viewsets.ModelViewSet):
    """
    CRUD JSON pour les stocks.
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    renderer_classes = [JSONRenderer]

class VenteViewSet(viewsets.ModelViewSet):
    """
    CRUD JSON pour les ventes.
    """
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer
    renderer_classes = [JSONRenderer]

class LigneVenteViewSet(viewsets.ModelViewSet):
    """
    CRUD JSON pour les lignes de vente.
    """
    queryset = LigneVente.objects.all()
    serializer_class = LigneVenteSerializer
    renderer_classes = [JSONRenderer]

class DemandeReapproViewSet(viewsets.ModelViewSet):
    """
    CRUD JSON pour les demandes de réapprovisionnement.
    """
    queryset = DemandeReappro.objects.all()
    serializer_class = DemandeReapproSerializer
    renderer_classes = [JSONRenderer]
