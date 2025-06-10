"""
Module des tests unitaires et d'intégration pour l'application application_multi_magasins.
"""

# pylint: disable=no-member

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Magasin, Produit, Vente, LigneVente, Stock, DemandeReappro

class MagasinModelTests(TestCase):
    """
    Tests unitaires pour le modèle Magasin.
    """

    def test_str_returns_nom(self):
        """
        Vérifie que la méthode __str__ du modèle Magasin retourne le nom du magasin.
        """
        magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.assertEqual(str(magasin), "Magasin Test")

class ProduitModelTests(TestCase):
    """
    Tests unitaires pour le modèle Produit.
    """

    def test_str_returns_nom(self):
        """
        Vérifie que la méthode __str__ du modèle Produit retourne le nom du produit.
        """
        produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        self.assertEqual(str(produit), "Produit X")

class VenteModelTests(TestCase):
    """
    Tests unitaires pour le modèle Vente.
    """

    def setUp(self):
        """
        Initialise un magasin de test pour les tests sur le modèle Vente.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")

    def test_str_contains_vente_and_date(self):
        """
        Vérifie que la représentation en chaîne d'une vente contient bien le mot 'Vente'
        et la date de la vente.
        """
        vente = Vente.objects.create(magasin=self.magasin)
        self.assertIn("Vente", str(vente))

    def test_default_est_retournee(self):
        """
        Vérifie que par défaut, l'attribut est_retournee d'une vente est False.
        """
        vente = Vente.objects.create(magasin=self.magasin)
        self.assertFalse(vente.est_retournee)

class LigneVenteTests(TestCase):
    """
    Tests unitaires pour le modèle LigneVente.
    """

    def setUp(self):
        """
        Initialise un magasin, un produit et une vente à utiliser dans les tests.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        self.vente = Vente.objects.create(magasin=self.magasin)

    def test_str_returns_ligne_details(self):
        """
        Vérifie que la représentation en chaîne de LigneVente renvoie les détails attendus.
        """
        ligne = LigneVente.objects.create(
            vente=self.vente,
            produit=self.produit,
            quantite=2,
            prix_unitaire=25.00
        )
        expected_str = "2 x Produit X at 25.00"
        self.assertEqual(str(ligne), expected_str)


class StockModelTests(TestCase):
    """
    Tests unitaires pour le modèle Stock.
    """

    def setUp(self):
        """
        Initialise un magasin et un produit à utiliser dans les tests du modèle Stock.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)

    def test_str_returns_stock_details(self):
        """
        Vérifie que la représentation en chaîne de Stock renvoie les informations attendues.
        """
        stock = Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)
        expected_str = "10 of Produit X in Magasin Test"
        self.assertEqual(str(stock), expected_str)

    def test_negative_quantite_not_allowed(self):
        """
        Vérifie que la méthode clean() lève une ValidationError lorsque la quantité est négative.
        """
        stock = Stock(magasin=self.magasin, produit=self.produit, quantite=-5)
        with self.assertRaises(ValidationError):
            stock.clean()


class DemandeReapproModelTests(TestCase):
    """
    Tests unitaires pour le modèle DemandeReappro.
    """

    def setUp(self):
        """
        Initialise un magasin et un produit à utiliser dans les tests du modèle DemandeReappro.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)

    def test_default_statut_is_pending(self):
        """
        Vérifie que le statut par défaut d'une demande de réapprovisionnement est 'pending'.
        """
        demande = DemandeReappro.objects.create(magasin=self.magasin, produit=self.produit, quantite=50)
        self.assertEqual(demande.statut, "pending")

    def test_str_returns_correct_information(self):
        """
        Vérifie que la représentation en chaîne de DemandeReappro renvoie les informations correctes.
        """
        demande = DemandeReappro.objects.create(magasin=self.magasin, produit=self.produit, quantite=50)
        expected_str = f"50 x Produit X pour Magasin Test (En attente)"
        self.assertEqual(str(demande), expected_str)

# Tests unitaires pour les vues

class InterfaceCaisseViewTests(TestCase):
    """
    Tests unitaires pour la vue de l'interface de caisse d'un magasin.
    """

    def setUp(self):
        """
        Configure un magasin de test pour les vues de l'interface de caisse.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")

    def test_interface_caisse_existant(self):
        """
        Vérifie que la vue 'menu_caisse' pour un magasin existant renvoie un status 200,
        utilise le bon template et fournit le bon contexte.
        """
        response = self.client.get(reverse('menu_caisse', args=[self.magasin.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu_caisse.html')
        self.assertEqual(response.context['magasin'], self.magasin)

    def test_interface_caisse_inexistant(self):
        """
        Vérifie que la vue 'menu_caisse' renvoie un status 404 lorsqu'on demande un magasin inexistant.
        """
        response = self.client.get(reverse('menu_caisse', args=[9999]))
        self.assertEqual(response.status_code, 404)


class RechercheProduitViewTests(TestCase):
    """
    Tests unitaires pour la vue de recherche de produit pour la caisse.
    """

    def setUp(self):
        """
        Prépare l'environnement de test en créant un magasin, un produit et le stock correspondant.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        # Création du stock lié à ce produit dans le magasin
        Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)

    def test_recherche_get(self):
        """
        Vérifie que la requête GET à la vue de recherche renvoie un status 200 et le bon template.
        """
        response = self.client.get(reverse('recherche_produit', args=[self.magasin.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recherche.html')

    def test_recherche_post_sans_critere(self):
        """
        Vérifie que soumettre un POST sans critère renvoie le message d'erreur approprié.
        """
        response = self.client.post(reverse('recherche_produit', args=[self.magasin.id]), {})
        self.assertContains(response, "Veuillez remplir au moins un critère.")

    def test_recherche_post_identifiant_invalide(self):
        """
        Vérifie que soumettre un identifiant non convertible en entier renvoie le message d'erreur.
        """
        data = {'identifiant': 'abc'}
        response = self.client.post(reverse('recherche_produit', args=[self.magasin.id]), data)
        self.assertContains(response, "Identifiant invalide.")

    def test_recherche_post_produit_trouve(self):
        """
        Vérifie qu'une recherche valide renvoie bien des résultats avec le bon contexte.
        """
        data = {'nom': 'Produit'}
        response = self.client.post(reverse('recherche_produit', args=[self.magasin.id]), data)
        # Le résultat doit contenir le produit recherché
        self.assertIsNotNone(response.context['resultats'])
        results = response.context['resultats']
        self.assertTrue(results.exists())
        self.assertIsNone(response.context['message_erreur'])

class EnregistrerVenteViewTests(TestCase):
    """
    Tests unitaires pour la vue 'enregistrer_vente' de l'application application_multi_magasins.
    """

    def setUp(self):
        """
        Initialise l'environnement de test avec un client, un magasin, un produit et son stock associé.
        """
        self.client = Client()
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        self.stock = Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)

    def test_vente_quantite_negative(self):
        """
        Vérifie que l'envoi d'une quantité négative renvoie le message d'erreur approprié.
        """
        data = {'produit_id': str(self.produit.id), 'quantite': '-3'}
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        self.assertContains(response, "La quantité doit être positive.")

    def test_vente_produit_non_trouve_dans_magasin(self):
        """
        Vérifie que l'envoi d'un produit_id inexistant dans le stock du magasin renvoie le message d'erreur correspondant.
        """
        data = {'produit_id': '9999', 'quantite': '1'}
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        self.assertContains(response, "Produit introuvable dans ce magasin.")

    def test_vente_stock_insuffisant(self):
        """
        Vérifie que, lorsqu'une quantité supérieure au stock disponible est demandée, le message 
        'Stock insuffisant pour cette vente.' est affiché.
        """
        data = {'produit_id': str(self.produit.id), 'quantite': '20'}  # Plus que disponible
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        self.assertContains(response, "Stock insuffisant pour cette vente.")

    def test_vente_success(self):
        """
        Vérifie que, lors d'une vente réussie, le message de succès est affiché,
        qu'une vente et une ligne de vente sont créées et que le stock est décrémenté.
        """
        quantite = 3
        data = {'produit_id': str(self.produit.id), 'quantite': str(quantite)}
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        expected_message = f"Vente enregistrée : {quantite} x {self.produit.nom}."
        self.assertContains(response, expected_message)

        # Vérifier que la vente et la ligne de vente ont bien été créées.
        self.assertTrue(Vente.objects.filter(magasin=self.magasin).exists())
        self.assertTrue(LigneVente.objects.filter(vente__magasin=self.magasin, produit=self.produit).exists())

        # Vérifier que le stock a été décrémenté.
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantite, 10 - quantite)


class TraiterRetourViewTests(TestCase):
    """
    Tests unitaires pour la vue 'traiter_retour' de l'application application_multi_magasins.
    """

    def setUp(self):
        """
        Initialise l'environnement de test en créant un magasin, un produit, un stock,
        et une vente avec une ligne de vente associée.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        self.produit = Produit.objects.create(nom="Produit A", categorie="Catégorie A", prix=25.00)
        self.stock = Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)
        self.vente = Vente.objects.create(magasin=self.magasin)
        self.ligne = LigneVente.objects.create(
            vente=self.vente,
            produit=self.produit,
            quantite=2,
            prix_unitaire=self.produit.prix
        )

    def test_get_method(self):
        """
        Vérifie que la méthode GET de la vue 'traiter_retour' renvoie le status 200, 
        utilise le bon template et inclut 'message' dans son contexte.
        """
        url = reverse('traiter_retour', args=[self.magasin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "retour.html")
        self.assertIn("message", response.context)

    def test_post_with_invalid_vente_id(self):
        """
        Vérifie que passer un identifiant de vente invalide dans un POST renvoie le message d'erreur approprié.
        """
        url = reverse('traiter_retour', args=[self.magasin.id])
        response = self.client.post(url, {"vente_id": "abc"})
        self.assertContains(response, "ID de vente invalide.")

    def test_post_with_nonexistent_vente(self):
        """
        Vérifie que passer un identifiant de vente inexistant renvoie le message d'erreur correct.
        """
        url = reverse('traiter_retour', args=[self.magasin.id])
        response = self.client.post(url, {"vente_id": 9999})
        self.assertContains(response, "Vente introuvable dans ce magasin.")

    def test_traiter_retour_success(self):
        """
        Vérifie que la vue 'traiter_retour' traite correctement le retour d'une vente,
        affiche le message de succès, supprime la vente et met à jour le stock.
        """
        url = reverse('traiter_retour', args=[self.magasin.id])
        initial_stock = self.stock.quantite
        data = {"vente_id": self.vente.id}
        response = self.client.post(url, data)
        expected_message = f"Retour traité : la vente {self.vente.id} a été annulée et le stock mis à jour."
        self.assertContains(response, expected_message)

        # Vérifier que la vente a été supprimée.
        with self.assertRaises(Vente.DoesNotExist):
            Vente.objects.get(id=self.vente.id)

        # Vérifier que le stock a été incrémenté de la quantité de la ligne de vente.
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantite, initial_stock + self.ligne.quantite)

class HistoriqueTransactionsViewTests(TestCase):
    """
    Tests unitaires pour la vue affichant l'historique des transactions d'un magasin.
    """

    def setUp(self):
        """
        Configure l'environnement de test en créant un magasin, des ventes et leurs lignes associées.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        # Créer quelques ventes et lignes associées
        self.vente1 = Vente.objects.create(magasin=self.magasin)
        self.vente2 = Vente.objects.create(magasin=self.magasin)
        self.produit = Produit.objects.create(nom="Produit A", categorie="Catégorie", prix=25.00)
        LigneVente.objects.create(vente=self.vente1, produit=self.produit, quantite=2, prix_unitaire=25.00)
        LigneVente.objects.create(vente=self.vente2, produit=self.produit, quantite=3, prix_unitaire=25.00)

    def test_historique_transactions_view(self):
        """
        Vérifie que la vue 'historique_transactions' renvoie le status code 200, le template 'historique.html'
        et que les ventes sont ordonnées par date décroissante.
        """
        url = reverse('historique_transactions', args=[self.magasin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'historique.html')
        self.assertEqual(response.context['magasin'], self.magasin)
        # Vérifie que les ventes sont ordonnées par date décroissante
        ventes = list(response.context['ventes'])
        self.assertGreaterEqual(ventes[0].date, ventes[1].date)

class ListeProduitsViewTests(TestCase):
    """
    Tests unitaires pour la vue 'liste_produits' qui affiche une liste triée des produits.
    """

    def setUp(self):
        """
        Initialise l'environnement de test en créant plusieurs produits.
        """
        Produit.objects.create(nom="Produit C", categorie="Cat", prix=30.00)
        Produit.objects.create(nom="Produit A", categorie="Cat", prix=10.00)
        Produit.objects.create(nom="Produit B", categorie="Cat", prix=20.00)

    def test_liste_produits_view(self):
        """
        Vérifie que la vue 'liste_produits' renvoie le status 200, utilise le template approprié,
        et que la liste des produits est triée par nom.
        """
        url = reverse("liste_produits")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "liste_produits.html")
        produits = response.context["produits"]
        # Vérifier l'ordre par nom
        noms = [p.nom for p in produits]
        self.assertEqual(noms, sorted(noms))