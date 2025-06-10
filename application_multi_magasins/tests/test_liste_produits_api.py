from rest_framework import status
from rest_framework.test import APITestCase
from application_multi_magasins.models import Produit
from application_multi_magasins.serializers import ProduitSerializer

class ListeProduitsAPIViewTest(APITestCase):
    def setUp(self):
        Produit.objects.create(nom="Apple", categorie="Fruit", prix="1.00")
        Produit.objects.create(nom="Banana", categorie="Fruit", prix="0.50")
        Produit.objects.create(nom="Carrot", categorie="Vegetable", prix="0.30")
        self.url = '/api/produit/list/'

    def test_get_liste_produits_json(self):
        """
        Vérifie que la requête GET au format JSON retourne une liste de produits
        correctement triée par nom.
        """
        response = self.client.get(self.url, format="json", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="La réponse JSON doit retourner un status 200 OK.")
                         
        produits = Produit.objects.all().order_by('nom')
        serializer = ProduitSerializer(produits, many=True)
        self.assertEqual(response.data, serializer.data,
                         msg="Les données retournées en JSON ne correspondent pas aux données attendues.")

    def test_get_liste_produits_html(self):
        """
        Vérifie que la requête GET au format HTML retourne la liste des produits
        en utilisant le template 'liste_produits.html'.
        """
        response = self.client.get(self.url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="La réponse HTML doit retourner un status 200 OK.")
                         
        template_names = [template.name for template in response.templates if template.name]
        self.assertIn("liste_produits.html", template_names,
                      msg="Le template utilisé doit être 'liste_produits.html'.")
                      
        self.assertIn("produits", response.data,
                      msg="Le contexte de la réponse HTML doit contenir la clé 'produits'.")
                      
        self.assertEqual(len(response.data["produits"]), Produit.objects.count(),
                         msg="Le contexte doit contenir tous les produits existants.")