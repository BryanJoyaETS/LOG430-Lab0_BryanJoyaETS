from rest_framework import status
from rest_framework.test import APITestCase
from application_multi_magasins.models import Magasin, Produit, Stock, DemandeReappro

class DemandeReapproActionAPIViewTest(APITestCase):
    def setUp(self):
        self.magasin_local = Magasin.objects.create(nom="Store1", adresse="123 Rue Local")
        self.produit = Produit.objects.create(nom="Product1", categorie="Catégorie1", prix="10.00")
        
        self.demande = DemandeReappro.objects.create(
            magasin=self.magasin_local,
            produit=self.produit,
            quantite=5,
            statut="pending",
        )
        
        self.central_magasin = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Center Address")
        self.central_stock = Stock.objects.create(
            magasin=self.central_magasin,
            produit=self.produit,
            quantite=20 
        )
        
        self.local_stock = Stock.objects.create(
            magasin=self.magasin_local,
            produit=self.produit,
            quantite=10
        )
        
        self.url = f'/api/demandes/{self.demande.id}/action/'

    def test_invalid_action(self):
        """
        Vérifie que l'action invalide retourne une erreur 400.
        """
        payload = {"action": "invalid"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Une action invalide doit retourner le status 400.")
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Action invalide.")

    def test_approve_success(self):
        """
        Vérifie qu'une demande approuvée transfère le stock :
          - La quantité du stock central est réduite correctement.
          - La quantité du stock local est incrémentée.
          - La demande est supprimée.
        """
        payload = {"action": "approve"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="L'approbation doit retourner le status 200.")
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "Demande approuvée, stock transféré du centre logistique avec succès."
        )
        self.assertFalse(DemandeReappro.objects.filter(id=self.demande.id).exists(),
                         msg="La demande doit être supprimée après approbation.")
        self.central_stock.refresh_from_db()
        self.assertEqual(self.central_stock.quantite, 15,
                         msg="Le stock central doit être réduit de la quantité demandée.")
        self.local_stock.refresh_from_db()
        self.assertEqual(self.local_stock.quantite, 15,
                         msg="Le stock local doit être incrémenté du montant de la demande.")

    def test_approve_missing_central_stock(self):
        """
        Vérifie que si le stock central pour le produit n'existe pas,
        l'API retourne une erreur 400.
        """
        self.central_stock.delete()
        payload = {"action": "approve"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="En l'absence de stock central, l'API doit retourner le status 400.")
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Stock central indisponible pour ce produit.")
        self.assertTrue(DemandeReappro.objects.filter(id=self.demande.id).exists(),
                        msg="La demande doit rester intacte si le stock central est inexistant.")

    def test_approve_insufficient_central_stock(self):
        """
        Vérifie que si le stock central est insuffisant par rapport à la quantité demandée,
        l'API retourne une erreur 400.
        """
        self.central_stock.quantite = 3
        self.central_stock.save()
        
        payload = {"action": "approve"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="Si le stock central est insuffisant, un status 400 doit être retourné.")
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Stock central insuffisant pour cette demande.")
        self.assertTrue(DemandeReappro.objects.filter(id=self.demande.id).exists(),
                        msg="La demande doit rester intacte si le stock central est insuffisant.")

    def test_refuse(self):
        """
        Vérifie que l'action 'refuse' supprime la demande et retourne un message approprié.
        """
        payload = {"action": "refuse"}
        response = self.client.post(self.url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="Le refus doit retourner le status 200.")
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Demande refusée avec succès.")
        self.assertFalse(DemandeReappro.objects.filter(id=self.demande.id).exists(),
                         msg="La demande doit être supprimée après refus.")