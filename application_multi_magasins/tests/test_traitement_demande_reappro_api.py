from rest_framework import status
from rest_framework.test import APITestCase
from application_multi_magasins.models import Magasin, Produit, DemandeReappro

#pylint:disable=no-member

class TraitementDemandeReapproAPIViewTest(APITestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Store1", adresse="123 Rue Store1")
        self.produit = Produit.objects.create(nom="Product1", categorie="Catégorie1", prix="10.00")
        
        self.demande1 = DemandeReappro.objects.create(
            magasin=self.magasin,
            produit=self.produit,
            quantite=10,
            statut="pending"
        )
        self.demande2 = DemandeReappro.objects.create(
            magasin=self.magasin,
            produit=self.produit,
            quantite=5,
            statut="pending"
        )
        self.url = '/api/demande/list/'

    def test_get_pending_demandes(self):
        """
        Vérifie que la requête GET retourne la liste des demandes en attente.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for demande in response.data["demandes"]:
            self.assertEqual(demande.statut, "pending", msg="Toutes les demandes retournées doivent être en état 'pending'.")

    def test_post_approve_demande(self):
        payload = {"demande_id": self.demande1.id, "action": "approve"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        msg="Le POST avec 'approve' doit retourner un 200 OK.")
        self.demande1.refresh_from_db()
        self.assertEqual(self.demande1.statut, "approved",
                        msg="Le statut de la demande doit être mis à 'approved'.")
        for demande in response.data.get("demandes", []):
            self.assertNotEqual(demande.id, self.demande1.id,
                                msg="La demande approuvée ne doit pas figurer dans la liste des demandes en attente.")

    def test_post_refuse_demande(self):
        payload = {"demande_id": self.demande2.id, "action": "refuse"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                        msg="Le POST avec 'refuse' doit retourner un 200 OK.")
        self.demande2.refresh_from_db()
        self.assertEqual(self.demande2.statut, "refused",
                        msg="Le statut de la demande doit être mis à 'refused'.")
        for demande in response.data.get("demandes", []):
            self.assertNotEqual(demande.id, self.demande2.id,
                                msg="La demande refusée ne doit pas figurer dans la liste des demandes en attente.")

    def test_post_invalid_action(self):
        """
        Vérifie que lorsque l'action envoyée est invalide, le statut de la demande reste 'pending'
        et que l'API retourne le contexte des demandes en attente.
        """
        payload = {"demande_id": self.demande1.id, "action": "invalid"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="Le POST avec une action invalide doit retourner un 200 OK, en renvoyant le contexte.")
        self.demande1.refresh_from_db()
        self.assertEqual(self.demande1.statut, "pending",
                         msg="Avec une action invalide, le statut de la demande doit rester 'pending'.")
        self.assertIn("demandes", response.data,
                      msg="La réponse doit contenir la clé 'demandes' même en cas d'action invalide.")