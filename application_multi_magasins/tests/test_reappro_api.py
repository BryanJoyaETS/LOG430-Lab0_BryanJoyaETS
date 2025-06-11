from rest_framework import status
from rest_framework.test import APITestCase
from application_multi_magasins.models import Magasin, Produit, Stock

#pylint:disable=no-member

class ReapproAPIViewTest(APITestCase):
    def setUp(self):
        self.magasin_local = Magasin.objects.create(nom="Store1", adresse="123 Rue Local")
        self.magasin_central = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="456 Rue Central")
        self.produit = Produit.objects.create(nom="Product1", categorie="Catégorie1", prix="10.00")
        
        self.stock_local = Stock.objects.create(magasin=self.magasin_local, produit=self.produit, quantite=20)
        self.stock_central = Stock.objects.create(magasin=self.magasin_central, produit=self.produit, quantite=50)

        self.url = f'/api/reappro/{self.stock_local.id}/?format=json'
    
    def test_reappro_api_with_central_stock(self):
        """
        Vérifie que l'API retourne correctement les informations en présence d'un magasin central.
        La réponse doit contenir :
          - les infos du produit,
          - les infos du magasin local,
          - 'stock_local' conforme,
          - 'stock_central' égal à la quantité du stock central.
        """
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         msg="La réponse devrait être 200 OK.")
        
        data = response.data
        self.assertIn('produit', data, msg="La clé 'produit' doit être présente dans la réponse.")
        self.assertIn('magasin', data, msg="La clé 'magasin' doit être présente dans la réponse.")
        self.assertIn('stock_local', data, msg="La clé 'stock_local' doit être présente dans la réponse.")
        self.assertIn('stock_central', data, msg="La clé 'stock_central' doit être présente dans la réponse.")
        
        self.assertEqual(data['stock_local'], 20, msg="La quantité locale doit être 20.")
        self.assertEqual(data['stock_central'], 50, msg="La quantité centrale doit être 50.")
        
        self.assertEqual(data['produit']['id'], self.produit.id, msg="L'ID du produit ne correspond pas.")
        self.assertEqual(data['produit']['nom'], self.produit.nom, msg="Le nom du produit ne correspond pas.")
        
        self.assertEqual(data['magasin']['id'], self.magasin_local.id, msg="L'ID du magasin local ne correspond pas.")
        self.assertEqual(data['magasin']['nom'], self.magasin_local.nom, msg="Le nom du magasin local ne correspond pas.")
    
    def test_reappro_api_without_central(self):
        """
        Vérifie que si le magasin central n'existe pas, l'API retourne stock_central à 0.
        """
        self.magasin_central.delete()
        
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         msg="La réponse devrait être 200 OK même sans magasin central.")
        
        data = response.data
        self.assertEqual(data['stock_central'], 0, msg="En l'absence du magasin central, stock_central doit être 0.")