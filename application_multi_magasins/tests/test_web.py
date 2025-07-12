from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from application_multi_magasins.models import (
    Magasin, Produit, Stock, Vente, LigneVente, DemandeReappro
)

class MagasinViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.m1 = Magasin.objects.create(nom='M1', adresse='Adr1')
        self.m2 = Magasin.objects.create(nom='M2', adresse='Adr2')

    def test_list_magasins(self):
        url = reverse('magasin-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_retrieve_magasin(self):
        url = reverse('magasin-detail', args=[self.m1.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()['nom'], 'M1')

class ProduitViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.prod_url = reverse('produit-list')

    def test_create_update_delete_produit(self):
        resp = self.client.post(self.prod_url,
                                {'nom': 'P1', 'categorie': 'Cat', 'prix': '12.50'},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        prod_id = resp.json()['id']
        detail = reverse('produit-detail', args=[prod_id])
        resp2 = self.client.patch(detail, {'prix': '15.00'}, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.json()['prix'], '15.00')
        resp3 = self.client.delete(detail)
        self.assertEqual(resp3.status_code, status.HTTP_204_NO_CONTENT)

class StockViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.mag = Magasin.objects.create(nom='M1', adresse='Adr1')
        self.prod = Produit.objects.create(nom='P2', categorie='C2', prix='5.00')
        self.url = reverse('stock-list')

    def test_create_and_retrieve_stock(self):
        resp = self.client.post(self.url,
                                {'magasin': self.mag.id, 'produit': self.prod.id, 'quantite': 7},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        stock_id = resp.json()['id']
        detail = reverse('stock-detail', args=[stock_id])
        resp2 = self.client.get(detail)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.json()['quantite'], 7)

class VenteViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.mag = Magasin.objects.create(nom='M4', adresse='Adr4')
        self.url = reverse('vente-list')

    def test_create_and_list_vente(self):
        resp = self.client.post(self.url, {'magasin': self.mag.id}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        vente_id = resp.json()['id']
        resp2 = self.client.get(self.url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertTrue(any(v['id'] == vente_id for v in resp2.json()))

class LigneVenteViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.mag = Magasin.objects.create(nom='M5', adresse='Adr5')
        self.prod = Produit.objects.create(nom='P3', categorie='Cat3', prix='3.00')
        vente = Venda = Vente.objects.create(magasin=self.mag)
        self.url = reverse('ligne-list')

    def test_create_and_list_ligne(self):
        resp = self.client.post(self.url,
                                {'vente': Vente.objects.first().id, 'produit': self.prod.id, 'quantite': 4},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        lv_id = resp.json()['id']
        resp2 = self.client.get(self.url)
        self.assertTrue(any(l['id'] == lv_id for l in resp2.json()))

class DemandeReapproViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.mag = Magasin.objects.create(nom='M6', adresse='Adr6')
        self.prod = Produit.objects.create(nom='P4', categorie='Cat4', prix='4.00')
        self.url = reverse('demande-list')

    def test_create_and_list_demande(self):
        resp = self.client.post(self.url,
                                {'magasin': self.mag.id, 'produit': self.prod.id, 'quantite': 5},
                                format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        demande_id = resp.json()['id']
        resp2 = self.client.get(self.url)
        self.assertTrue(any(d['id'] == demande_id for d in resp2.json()))
