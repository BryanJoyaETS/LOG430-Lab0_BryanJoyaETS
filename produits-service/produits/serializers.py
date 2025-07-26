"""
Sérialiseurs pour transformer les modèles en JSON.

Ce module contient les classes de sérialisation pour les modèles principaux de l'application,
permettant la conversion entre les objets Django et les représentations JSON pour l'API REST.
"""
# pylint: disable=too-few-public-methods
from rest_framework import serializers
from .models import Magasin, Produit, Vente, LigneVente, Stock, DemandeReappro

class MagasinSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Magasin.
    Permet de convertir les instances de Magasin en JSON et inversement.
    """
    class Meta:
        model = Magasin
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Produit.
    Permet de convertir les instances de Produit en JSON et inversement.
    """
    class Meta:
        model = Produit
        fields = '__all__'

class VenteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Vente.
    Permet de convertir les instances de Vente en JSON et inversement.
    """
    class Meta:
        model = Vente
        fields = '__all__'

class LigneVenteSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle LigneVente.
    Permet de convertir les instances de LigneVente en JSON et inversement.
    """
    class Meta:
        model = LigneVente
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Stock.
    Permet de convertir les instances de Stock en JSON et inversement.
    Inclut les relations liées grâce à l'option depth.
    """
    class Meta:
        model = Stock
        fields = '__all__'
        depth = 1

class DemandeReapproSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle DemandeReappro.
    Sérialise aussi les objets liés Magasin et Produit en lecture seule.
    """
    magasin = MagasinSerializer(read_only=True)
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = DemandeReappro
        fields = '__all__'

## Laboratoire 6 : Sérialiseur pour la saga
class VenteLineInSerializer(serializers.Serializer):
    produit_id = serializers.UUIDField()
    quantite   = serializers.IntegerField(min_value=1)
    prix_unit  = serializers.DecimalField(max_digits=10, decimal_places=2)

class VenteCreateSerializer(serializers.Serializer):
    magasin_id = serializers.UUIDField()
    lignes     = VenteLineInSerializer(many=True)