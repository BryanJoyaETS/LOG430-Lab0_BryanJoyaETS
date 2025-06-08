"""
sérialiseurs pour transformer les modèles en JSON
"""
# application_multi_magasins/serializers.py
from rest_framework import serializers
from .models import Magasin, Produit, Vente, LigneVente, Stock, DemandeReappro

class MagasinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magasin
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'

class VenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vente
        fields = '__all__'

class LigneVenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneVente
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
        depth = 1

class DemandeReapproSerializer(serializers.ModelSerializer):
    magasin = MagasinSerializer(read_only=True)
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = DemandeReappro
        fields = '__all__'
        