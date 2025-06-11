from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

#pylint:disable=no-member

from application_multi_magasins.models import (
    Produit, Magasin, Stock, Vente, LigneVente, DemandeReappro
)

class ProduitAPITest(APITestCase):
    def setUp(self):
        self.list_url = reverse('produit-list')
        self.valid_data = {
            'nom': 'ProduitTest',
            'categorie': 'CatégorieTest',
            'prix': '9.99'
        }

    def test_create_produit(self):
        response = self.client.post(self.list_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Produit.objects.count(), 1)
        self.assertEqual(Produit.objects.get().nom, 'ProduitTest')

    def test_list_produit(self):
        Produit.objects.create(**self.valid_data)
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_produit(self):
        produit = Produit.objects.create(**self.valid_data)
        detail_url = reverse('produit-detail', kwargs={'pk': produit.pk})
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], produit.nom)

    def test_update_produit(self):
        produit = Produit.objects.create(**self.valid_data)
        detail_url = reverse('produit-detail', kwargs={'pk': produit.pk})
        update_data = {'nom': 'ProduitMisAJour', 'categorie': 'CatégorieTest', 'prix': '12.34'}
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        produit.refresh_from_db()
        self.assertEqual(produit.nom, 'ProduitMisAJour')

    def test_delete_produit(self):
        produit = Produit.objects.create(**self.valid_data)
        detail_url = reverse('produit-detail', kwargs={'pk': produit.pk})
        response = self.client.delete(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Produit.objects.count(), 0)

class MagasinAPITest(APITestCase):
    def setUp(self):
        self.list_url = reverse('magasin-list')
        self.valid_data = {
            'nom': 'MagasinTest',
            'adresse': '123 Rue Test'
        }

    def test_create_magasin(self):
        response = self.client.post(self.list_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Magasin.objects.count(), 1)
        self.assertEqual(Magasin.objects.get().nom, 'MagasinTest')

    def test_list_magasin(self):
        Magasin.objects.create(**self.valid_data)
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_magasin(self):
        magasin = Magasin.objects.create(**self.valid_data)
        detail_url = reverse('magasin-detail', kwargs={'pk': magasin.pk})
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], magasin.nom)

    def test_update_magasin(self):
        magasin = Magasin.objects.create(**self.valid_data)
        detail_url = reverse('magasin-detail', kwargs={'pk': magasin.pk})
        update_data = {'nom': 'MagasinMisAJour', 'adresse': '123 Rue Test'}
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        magasin.refresh_from_db()
        self.assertEqual(magasin.nom, 'MagasinMisAJour')

    def test_delete_magasin(self):
        magasin = Magasin.objects.create(**self.valid_data)
        detail_url = reverse('magasin-detail', kwargs={'pk': magasin.pk})
        response = self.client.delete(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Magasin.objects.count(), 0)

class StockAPITest(APITestCase):
    def setUp(self):
        self.list_url = reverse('stock-list')
        self.produit = Produit.objects.create(nom='ProduitTest', categorie='CatégorieTest', prix='9.99')
        self.magasin = Magasin.objects.create(nom='MagasinTest', adresse='123 Rue Test')
        self.valid_data = {
            'produit': self.produit.pk,
            'magasin': self.magasin.pk,
            'quantite': 10
        }

    def test_list_stock(self):
        Stock.objects.create(produit=self.produit, magasin=self.magasin, quantite=10)
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_stock(self):
        stock = Stock.objects.create(produit=self.produit, magasin=self.magasin, quantite=10)
        detail_url = reverse('stock-detail', kwargs={'pk': stock.pk})
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantite'], 10)

    def test_update_stock(self):
        stock = Stock.objects.create(produit=self.produit, magasin=self.magasin, quantite=10)
        detail_url = reverse('stock-detail', kwargs={'pk': stock.pk})
        update_data = {
            'produit': self.produit.pk,
            'magasin': self.magasin.pk,
            'quantite': 20
        }
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stock.refresh_from_db()
        self.assertEqual(stock.quantite, 20)

    def test_delete_stock(self):
        stock = Stock.objects.create(produit=self.produit, magasin=self.magasin, quantite=10)
        detail_url = reverse('stock-detail', kwargs={'pk': stock.pk})
        response = self.client.delete(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Stock.objects.count(), 0)

class VenteAPITest(APITestCase):
    def setUp(self):
        self.list_url = reverse('vente-list')
        self.magasin = Magasin.objects.create(nom='MagasinTest', adresse='123 Rue Test')
        self.valid_data = {
            'magasin': self.magasin.pk,
            'est_retournee': False
        }

    def test_create_vente(self):
        response = self.client.post(self.list_url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vente.objects.count(), 1)
        self.assertEqual(Vente.objects.get().magasin.pk, self.magasin.pk)

    def test_list_vente(self):
        Vente.objects.create(magasin=self.magasin, est_retournee=False)
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_vente(self):
        vente = Vente.objects.create(magasin=self.magasin, est_retournee=False)
        detail_url = reverse('vente-detail', kwargs={'pk': vente.pk})
        response = self.client.get(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_vente(self):
        vente = Vente.objects.create(magasin=self.magasin, est_retournee=False)
        detail_url = reverse('vente-detail', kwargs={'pk': vente.pk})
        update_data = {'magasin': self.magasin.pk, 'est_retournee': True}
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vente.refresh_from_db()
        self.assertTrue(vente.est_retournee)

    def test_delete_vente(self):
        vente = Vente.objects.create(magasin=self.magasin, est_retournee=False)
        detail_url = reverse('vente-detail', kwargs={'pk': vente.pk})
        response = self.client.delete(detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vente.objects.count(), 0)
