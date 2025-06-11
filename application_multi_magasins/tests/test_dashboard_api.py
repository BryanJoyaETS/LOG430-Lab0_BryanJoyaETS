from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from application_multi_magasins.models import Magasin, Produit, Vente, LigneVente, Stock

#pylint:disable=no-member

class DashboardAPIViewTest(APITestCase):
    def setUp(self):
        self.centre = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Center Address")
        
        self.store1 = Magasin.objects.create(nom="Store1", adresse="123 Street")
        self.store2 = Magasin.objects.create(nom="Store2", adresse="456 Avenue")
        
        self.product1 = Produit.objects.create(nom="Product1", categorie="Cat1", prix="10.00")
        self.product2 = Produit.objects.create(nom="Product2", categorie="Cat2", prix="20.00")
        
        self.vente1 = Vente.objects.create(magasin=self.store1, est_retournee=False)
        LigneVente.objects.create(
            vente=self.vente1,
            produit=self.product1,
            quantite=2,
            prix_unitaire="10.00"
        )
        LigneVente.objects.create(
            vente=self.vente1,
            produit=self.product2,
            quantite=3,
            prix_unitaire="20.00"
        )
        
        self.vente2 = Vente.objects.create(magasin=self.store2, est_retournee=False)
        LigneVente.objects.create(
            vente=self.vente2,
            produit=self.product2,
            quantite=1,
            prix_unitaire="20.00"
        )

        # Pour tester les ruptures, on crée un stock avec quantite <= 5.
        Stock.objects.create(magasin=self.store1, produit=self.product1, quantite=3)
        # Pour tester le surstock, on crée un stock avec quantite >= 100.
        Stock.objects.create(magasin=self.store1, produit=self.product2, quantite=150)
        Stock.objects.create(magasin=self.centre, produit=self.product1, quantite=99)
        
        now = timezone.now()
        self.vente1.date = now - timedelta(days=3)
        self.vente1.save()
        self.vente2.date = now - timedelta(days=2)
        self.vente2.save()

        self.json_url = '/api/dashboard/?format=json'
        self.html_url = '/api/dashboard/'

    def test_dashboard_json(self):
        """
        Vérifie que l'API retourne bien une réponse JSON contenant :
          - 'chiffre_affaires'
          - 'ruptures_stock'
          - 'surstock'
          - 'tendances'
        Le test s'assure également que ces valeurs sont bien des listes.
        """
        response = self.client.get(self.json_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         msg="La réponse JSON devrait retourner un status 200 OK.")
        data = response.data
        self.assertIn('chiffre_affaires', data, msg="La clé 'chiffre_affaires' n'est pas présente.")
        self.assertIn('ruptures_stock', data, msg="La clé 'ruptures_stock' n'est pas présente.")
        self.assertIn('surstock', data, msg="La clé 'surstock' n'est pas présente.")
        self.assertIn('tendances', data, msg="La clé 'tendances' n'est pas présente.")
        
        self.assertIsInstance(data['chiffre_affaires'], list, msg="'chiffre_affaires' doit être une liste.")
        self.assertIsInstance(data['ruptures_stock'], list, msg="'ruptures_stock' doit être une liste.")
        self.assertIsInstance(data['surstock'], list, msg="'surstock' doit être une liste.")
        self.assertIsInstance(data['tendances'], list, msg="'tendances' doit être une liste.")

    def test_dashboard_html(self):
        """
        Vérifie que l'API retourne bien une réponse HTML avec le template 'tableau_de_bord.html'.
        """
        response = self.client.get(self.html_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, status.HTTP_200_OK, 
                         msg="La réponse HTML devrait retourner un status 200 OK.")
        template_names = [template.name for template in response.templates if template.name]
        self.assertIn('tableau_de_bord.html', template_names,
                      msg="Le template 'tableau_de_bord.html' doit être utilisé pour la réponse HTML.")