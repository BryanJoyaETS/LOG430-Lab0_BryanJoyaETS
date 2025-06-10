from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from application_multi_magasins.models import Produit
from application_multi_magasins.serializers import ProduitSerializer

class ModifierProduitAPIViewTest(APITestCase):
    def setUp(self):
        self.produit = Produit.objects.create(
            nom="ProduitTest",
            categorie="CatégorieTest",
            prix="10.00"
        )
        self.url = f'/api/produit/{self.produit.id}/modifier/'

    def test_get_produit_json(self):
        """
        GET en format JSON : la vue doit retourner les détails du produit sérialisé.
        """
        response = self.client.get(self.url, format='json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="GET JSON doit retourner status 200 OK.")
        serializer = ProduitSerializer(self.produit)
        self.assertEqual(response.data, serializer.data,
                         msg="Les données retournées ne correspondent pas à la sérialisation attendue.")

    def test_get_produit_html(self):
        """
        GET en format HTML : la vue doit retourner le contexte incluant le produit et utiliser le template.
        """
        response = self.client.get(self.url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="GET HTML doit retourner status 200 OK.")
        template_names = [t.name for t in response.templates if t.name]
        self.assertIn("modifier_produit.html", template_names,
                      msg="Le template 'modifier_produit.html' doit être utilisé pour la réponse HTML.")
        self.assertIn("produit", response.data,
                      msg="Le contexte de la réponse HTML doit contenir la clé 'produit'.")
        self.assertEqual(response.data["produit"].id, self.produit.id,
                         msg="L'ID du produit dans le contexte ne correspond pas.")

    def test_put_produit_valid_json(self):
        """
        PUT (JSON) : Envoi d'une mise à jour partielle avec données valides (mise à jour du nom).
        La réponse doit refléter le produit modifié.
        """
        payload = {"nom": "ProduitModifie"}
        response = self.client.put(self.url, data=payload, format="json", HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="PUT JSON valide doit retourner 200 OK.")
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.nom, "ProduitModifie",
                         msg="Le nom du produit n'a pas été mis à jour correctement.")
        serializer = ProduitSerializer(self.produit)
        self.assertEqual(response.data, serializer.data,
                         msg="Les données de la réponse ne correspondent pas au produit mis à jour.")

    def test_put_produit_valid_html(self):
        """
        PUT (HTML) : Mise à jour avec données valides en HTML.
        La réponse doit utiliser le template et comporter le message de succès.
        """
        payload = {"categorie": "NouvelleCatégorie"}
        response = self.client.put(self.url, data=payload, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="PUT HTML valide doit retourner 200 OK.")
        template_names = [t.name for t in response.templates if t.name]
        self.assertIn("modifier_produit.html", template_names,
                      msg="Le template utilisé doit être 'modifier_produit.html'.")
        self.assertIn("message", response.data,
                      msg="La réponse HTML doit contenir le message de succès.")
        self.assertEqual(response.data["message"], "Produit mis à jour avec succès !",
                         msg="Le message de succès ne correspond pas.")
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.categorie, "NouvelleCatégorie",
                         msg="La catégorie du produit n'a pas été mise à jour correctement.")

    def test_put_produit_invalid_json(self):
        """
        PUT (JSON) : Envoi de données invalides ; la réponse doit renvoyer des erreurs et status 400.
        Par exemple, fournir une valeur non numérique pour le prix.
        """
        payload = {"prix": "invalide"}
        response = self.client.put(self.url, data=payload, format="json", HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg="PUT JSON invalide doit retourner 400 BAD REQUEST.")
        self.assertTrue("prix" in response.data,
                        msg="La réponse doit contenir une erreur relative au champ 'prix'.")

    def test_put_produit_invalid_html(self):
        """
        PUT (HTML) : Envoi de données invalides avec le format HTML.
        Le contexte de la réponse doit contenir une clé 'errors' avec les messages d'erreur.
        """
        payload = {"prix": "invalide"}
        response = self.client.put(self.url, data=payload, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                        msg="PUT HTML invalide doit retourner 400 BAD REQUEST.")
        self.assertIn("errors", response.data,
                    msg="La réponse HTML doit contenir la clé 'errors' en cas d'erreur.")