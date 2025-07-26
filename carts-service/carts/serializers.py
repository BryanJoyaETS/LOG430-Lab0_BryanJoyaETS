# carts/serializers.py
from rest_framework import serializers
from .models import Magasin, Produit, Stock, Vente, LigneVente, Cart, CartLine


class MagasinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magasin
        fields = ['id', 'nom', 'adresse']

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'categorie', 'prix']

class StockSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    class Meta:
        model = Stock
        fields = ['id', 'magasin', 'produit', 'quantite']

class LigneVenteSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)
    class Meta:
        model = LigneVente
        fields = ['id', 'produit', 'quantite', 'prix_unitaire']

class VenteSerializer(serializers.ModelSerializer):
    lignes = LigneVenteSerializer(many=True, read_only=True)
    class Meta:
        model = Vente
        fields = ['id', 'date', 'magasin', 'est_retournee', 'lignes']

from rest_framework import serializers
from .models import DemandeReappro

class DemandeReapproSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeReappro
        fields = ['id','magasin','produit','quantite','statut','date_demande','date_traitement']

class CartLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartLine
        fields = ["produit_id", "quantite"]

class CartSerializer(serializers.ModelSerializer):
    lines = CartLineSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ["id", "magasin_id", "status", "lines"]

