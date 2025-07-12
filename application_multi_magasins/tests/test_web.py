"""
Tests pour les ViewSets de l'application application_multi_magasins
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from application_multi_magasins.models import (
    DemandeReappro,
    LigneVente,
    Magasin,
    Produit,
    Stock,
    Vente,
)


class MagasinViewSetTest(APITestCase):
    """Tests pour le ViewSet Magasin"""

    def setUp(self):
        self.client = APIClient()
        Magasin.objects.create(nom="M1", adresse="Adr1")
        Magasin.objects.create(nom="M2", adresse="Adr2")

    def test_list_magasins(self):
        url = reverse('magasin-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_retrieve_magasin(self):
        magasin = Magasin.objects.first()
        url = reverse('magasin-detail', args=[magasin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['nom'], magasin.nom)


class ProduitViewSetTest(APITestCase):
    """Tests pour le ViewSet Produit"""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('produit-list')

    def test_create_update_delete(self):
        payload = {'nom': 'P1', 'categorie': 'Cat', 'prix': '12.50'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        produit_id = response.json()['id']

        detail_url = reverse('produit-detail', args=[produit_id])
        update_payload = {'prix': '15.00'}
        response = self.client.patch(detail_url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['prix'], '15.00')

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class StockViewSetTest(APITestCase):
    """Tests CRUD pour Stock via API (seulement lecture, create via ORM)."""

    def setUp(self):
        self.client = APIClient()
        self.mag = Magasin.objects.create(nom='M1', adresse='Adr1')
        self.prod = Produit.objects.create(nom='P2', categorie='C2', prix='5.00')
        self.stock = Stock.objects.create(magasin=self.mag, produit=self.prod, quantite=7)

    def test_list_stock(self):
        url = reverse('stock-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(any(item['id'] == self.stock.id for item in data))

    def test_retrieve_stock(self):
        url = reverse('stock-detail', args=[self.stock.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['quantite'], 7)

class VenteViewSetTest(APITestCase):
    """Tests pour le ViewSet Vente"""

    def setUp(self):
        self.client = APIClient()
        magasin = Magasin.objects.create(nom='M4', adresse='Adr4')
        self.url = reverse('vente-list')
        self.magasin = magasin

    def test_create_and_list_vente(self):
        payload = {'magasin': self.magasin.id}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        vente_id = response.json()['id']

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(any(item['id'] == vente_id for item in data))


class LigneVenteViewSetTest(APITestCase):
    """Tests pour le ViewSet LigneVente"""

    def setUp(self):
        self.client = APIClient()
        magasin = Magasin.objects.create(nom='M5', adresse='Adr5')
        produit = Produit.objects.create(nom='P3', categorie='Cat3', prix='3.00')
        self.vente = Vente.objects.create(magasin=magasin)
        self.url = reverse('ligne-list')
        self.produit = produit

    
class DemandeReapproViewSetTest(APITestCase):
    """Tests CRUD pour DemandeReappro via API (seulement lecture, create via ORM)."""

    def setUp(self):
        self.client = APIClient()
        self.mag = Magasin.objects.create(nom='M6', adresse='Adr6')
        self.prod = Produit.objects.create(nom='P4', categorie='Cat4', prix='4.00')
        self.demande = DemandeReappro.objects.create(
            magasin=self.mag, produit=self.prod, quantite=5, statut='pending'
        )

    def test_list_demandes(self):
        url = reverse('demande-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(any(item['id'] == self.demande.id for item in data))

    def test_retrieve_demande(self):
        url = reverse('demande-detail', args=[self.demande.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['quantite'], 5)
