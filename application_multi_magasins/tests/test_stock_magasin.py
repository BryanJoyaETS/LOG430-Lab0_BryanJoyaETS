from rest_framework import status
from rest_framework.test import APITestCase
from application_multi_magasins.models import Magasin, Produit, Stock
from application_multi_magasins.serializers import MagasinSerializer, StockSerializer

#pylint:disable=no-member

class StockMagasinAPIViewTest(APITestCase):
    def setUp(self):
        self.central = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Center Address")
        
        self.store = Magasin.objects.create(nom="Store1", adresse="123 Rue Store1")
        
        self.produit1 = Produit.objects.create(nom="Product1", categorie="Cat1", prix="10.00")
        self.produit2 = Produit.objects.create(nom="Product2", categorie="Cat2", prix="20.00")
        
        self.stock1 = Stock.objects.create(magasin=self.store, produit=self.produit1, quantite=50)
        self.stock2 = Stock.objects.create(magasin=self.store, produit=self.produit2, quantite=30)
        
        self.center_stock1 = Stock.objects.create(magasin=self.central, produit=self.produit1, quantite=100)
        self.center_stock2 = Stock.objects.create(magasin=self.central, produit=self.produit2, quantite=150)
        
        self.json_url = f'/api/stock/{self.store.id}/?format=json'
        self.html_url = f'/api/stock/{self.store.id}/'
    
    def test_stock_magasin_json(self):
        """
        Vérifier que l'API retourne bien le stock du magasin au format JSON.
        La réponse doit contenir les clés "magasin", "stocks" et "central_stocks" avec 
        des données sérialisées correspondantes.
        """
        response = self.client.get(self.json_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         msg="La réponse JSON devrait être en HTTP 200 OK.")
        
        data = response.data
        self.assertIn('magasin', data, msg="La clé 'magasin' est absente dans la réponse JSON.")
        self.assertIn('stocks', data, msg="La clé 'stocks' est absente dans la réponse JSON.")
        self.assertIn('central_stocks', data, msg="La clé 'central_stocks' est absente dans la réponse JSON.")
        
        expected_magasin = MagasinSerializer(self.store).data
        self.assertEqual(data['magasin'], expected_magasin,
                         msg="La sérialisation du magasin ne correspond pas à ce qui est attendu.")
        
        self.assertEqual(len(data['stocks']), 2,
                         msg="Le nombre de stocks pour le magasin n'est pas correct.")
        
        self.assertEqual(len(data['central_stocks']), 2,
                         msg="Le nombre de stocks du centre n'est pas correct.")

    def test_stock_magasin_html(self):
        """
        Vérifier que l'API retourne bien le stock du magasin au format HTML.
        La réponse doit utiliser le template 'stock_magasin.html'.
        """
        response = self.client.get(self.html_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="La réponse HTML devrait être en HTTP 200 OK.")
        template_names = [t.name for t in response.templates]
        self.assertIn('stock_magasin.html', template_names,
                      msg="Le template 'stock_magasin.html' ne fait pas partie des templates utilisés.")