from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from application_multi_magasins.models import Magasin, Produit, Stock, DemandeReappro

#pylint:disable=no-member


class DemandeReapproAPIViewTest(APITestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Store1", adresse="123 Rue Store1")
        self.produit = Produit.objects.create(nom="Product1", categorie="Catégorie1", prix="10.00")
        self.stock = Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=20)
        self.url = f'/api/demande_reappro_utilisateur/{self.stock.id}/'

    def test_post_valid_quantite(self):
        """
        Teste la création d'une demande de réapprovisionnement avec une quantité valide.
        La réponse doit contenir un message de succès et le status 201.
        """
        payload = {'quantite': '5'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg="La requête avec une quantité valide doit retourner le status 201.")
        self.assertIn('message', response.data, msg="La réponse doit contenir le message de succès.")
        self.assertIn('magasin_id', response.data, msg="La réponse doit contenir l'ID du magasin.")
        self.assertEqual(response.data['message'], 'Demande de réapprovisionnement soumise avec succès.')
        self.assertEqual(DemandeReappro.objects.filter(magasin=self.magasin, produit=self.produit).count(), 1)

    def test_post_missing_quantite(self):
        """
        Teste le POST sans fournir la quantité. L'API doit retourner un error avec status 400.
        """
        payload = {}  
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="L'absence de 'quantite' doit retourner le status 400.")
        self.assertIn('error', response.data, msg="La réponse doit contenir le message d'erreur.")
        self.assertEqual(response.data['error'], 'Quantité non spécifiée')

    def test_post_invalid_quantite(self):
        """
        Teste le POST avec une quantité invalide (par exemple, une valeur non convertible ou < 1).
        L'API doit retourner une erreur avec status 400.
        """
        payload = {'quantite': 'abc'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Une quantité non convertible doit retourner le status 400.")
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Quantité invalide')

        payload = {'quantite': '0'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Une quantité inférieure à 1 doit retourner le status 400.")
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Quantité invalide')