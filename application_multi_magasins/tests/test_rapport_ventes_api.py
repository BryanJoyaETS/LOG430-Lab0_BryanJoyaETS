from django.urls import reverse
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from rest_framework import status
from rest_framework.test import APITestCase

from application_multi_magasins.models import Magasin, Produit, Vente, LigneVente, Stock

#pylint:disable=no-member

class RapportVentesAPIViewTest(APITestCase):
    def setUp(self):
        self.centre = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Centre Address")
        self.store1 = Magasin.objects.create(nom="Store1", adresse="123 Rue Store1")

        self.produit1 = Produit.objects.create(nom="Product1", categorie="Category1", prix="10.00")
        self.produit2 = Produit.objects.create(nom="Product2", categorie="Category2", prix="20.00")
        
        self.vente1 = Vente.objects.create(magasin=self.store1, est_retournee=False)
        LigneVente.objects.create(
            vente=self.vente1,
            produit=self.produit1,
            quantite=5,
            prix_unitaire="10.00"
        )
        LigneVente.objects.create(
            vente=self.vente1,
            produit=self.produit2,
            quantite=3,
            prix_unitaire="20.00"
        )
        Stock.objects.create(magasin=self.store1, produit=self.produit1, quantite=100)
        Stock.objects.create(magasin=self.store1, produit=self.produit2, quantite=50)

    def test_rapport_ventes_json(self):
        """
        Teste l'API RapportVentesAPIView en demandant une réponse JSON.
        Vérifie que la réponse contient les clés 'ventes_par_magasin',
        'produits_populaires' et 'stock_restant' et que ces valeurs sont listes.
        """
        url = '/api/rapport/?format=json'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="La réponse devrait être 200 OK.")
        
        json_data = response.data
        self.assertIn('ventes_par_magasin', json_data, msg="La clé 'ventes_par_magasin' est absente.")
        self.assertIn('produits_populaires', json_data, msg="La clé 'produits_populaires' est absente.")
        self.assertIn('stock_restant', json_data, msg="La clé 'stock_restant' est absente.")
        
        self.assertIsInstance(json_data['ventes_par_magasin'], list, msg="'ventes_par_magasin' devrait être une liste.")
        self.assertIsInstance(json_data['produits_populaires'], list, msg="'produits_populaires' devrait être une liste.")
        self.assertIsInstance(json_data['stock_restant'], list, msg="'stock_restant' devrait être une liste.")

    def test_rapport_ventes_html(self):
        """
        Teste l'API en demandant une réponse HTML afin de s'assurer que le rendu
        via le template fonctionne correctement.
        """
        url = '/api/rapport/'
        response = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg="La réponse HTML devrait être 200 OK.")
        self.assertIn('rapport_de_ventes.html', [t.name for t in response.templates], msg="Le template utilisé doit être 'rapport_de_ventes.html'.")