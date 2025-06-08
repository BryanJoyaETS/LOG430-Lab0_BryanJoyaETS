"""
Module des tests unitaires et d'intégration pour l'application application_multi_magasins.
"""

# pylint: disable=no-member

import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from .models import Magasin, Produit, Vente, LigneVente, Stock, DemandeReappro

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

class AfficherMagasinsViewTests(TestCase):
    """
    Tests unitaires pour la vue qui affiche la liste paginée des magasins.
    """

    def setUp(self):
        """
        Prépare l'environnement de test en créant 15 magasins pour tester la pagination.
        """
        # Créer plus de 10 magasins pour tester la pagination.
        for i in range(15):
            Magasin.objects.create(nom=f"Magasin {i}", adresse="123 Rue Test")

    def test_afficher_magasins_status_et_template(self):
        """
        Vérifie que la vue 'afficher_magasins' renvoie un status 200, utilise le bon template
        et que la première page affiche 10 magasins.
        """
        response = self.client.get(reverse('index'))  # Assurez-vous de définir le nom 'index' dans urls.py.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        # Vérifier que nous avons bien 10 éléments sur la première page
        self.assertEqual(len(response.context['magasins']), 10)


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

class StockMagasinViewTests(TestCase):
    """
    Tests unitaires pour la vue de consultation du stock d'un magasin.
    """

    def setUp(self):
        """
        Configure l'environnement de test : crée un magasin et plusieurs stocks associés.
        """
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        # Créer plusieurs stocks
        self.produit1 = Produit.objects.create(nom="Produit A", categorie="Catégorie", prix=25.00)
        self.produit2 = Produit.objects.create(nom="Produit B", categorie="Catégorie", prix=30.00)
        Stock.objects.create(magasin=self.magasin, produit=self.produit1, quantite=5)
        Stock.objects.create(magasin=self.magasin, produit=self.produit2, quantite=15)

    def test_stock_magasin_view(self):
        """
        Vérifie que la vue 'stock_magasin' renvoie le status code 200, le bon template
        et que le contexte contient la liste correcte de stocks pour le magasin.
        """
        url = reverse('stock_magasin', args=[self.magasin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stock_magasin.html')
        # Vérifier que le contexte contient bien la liste de stocks
        self.assertIn('stocks', response.context)
        self.assertEqual(response.context['magasin'], self.magasin)
        self.assertEqual(response.context['stocks'].count(), 2)


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


class GenererRapportViewTests(TestCase):
    """
    Tests unitaires pour la vue 'generer_rapport' qui génère le rapport consolidé des ventes.
    """

    def setUp(self):
        """
        Configure l'environnement de test en créant le centre logistique, d'autres magasins,
        des produits, des ventes et des stocks pour générer le rapport.
        """
        # Créer le centre logistique
        self.centre = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Adresse Centre")
        # Créer d'autres magasins
        self.magasin1 = Magasin.objects.create(nom="Magasin A", adresse="Adresse A")
        self.magasin2 = Magasin.objects.create(nom="Magasin B", adresse="Adresse B")
        # Créer des produits et ventes pour ces magasins
        self.produit = Produit.objects.create(nom="Produit A", categorie="Catégorie", prix=10.00)
        # Vente pour magasin1
        vente1 = Vente.objects.create(magasin=self.magasin1)
        LigneVente.objects.create(vente=vente1, produit=self.produit, quantite=5, prix_unitaire=10.00)
        # Vente pour magasin2
        vente2 = Vente.objects.create(magasin=self.magasin2)
        LigneVente.objects.create(vente=vente2, produit=self.produit, quantite=3, prix_unitaire=10.00)
        # Créer des stocks
        Stock.objects.create(magasin=self.magasin1, produit=self.produit, quantite=20)
        Stock.objects.create(magasin=self.magasin2, produit=self.produit, quantite=15)

    def test_generer_rapport_view(self):
        """
        Vérifie que la vue 'generer_rapport' renvoie le status code 200, le template 'rapport_de_ventes.html'
        et que le contexte inclut les clés 'ventes_par_magasin', 'produits_populaires' et 'stock_restant'.
        """
        url = reverse('generer_rapport')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rapport_de_ventes.html')
        self.assertIn('ventes_par_magasin', response.context)
        self.assertIn('produits_populaires', response.context)
        self.assertIn('stock_restant', response.context)


class TableauBordViewTests(TestCase):
    """
    Tests unitaires pour la vue 'tableau_bord' qui affiche le tableau de bord synthétique.
    """

    def setUp(self):
        """
        Configure l'environnement de test en créant le centre logistique, un magasin, un produit,
        des stocks et des ventes pour le calcul du tableau de bord.
        """
        # Créer le centre logistique et un magasin
        self.centre = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Adresse Centre")
        self.magasin = Magasin.objects.create(nom="Magasin A", adresse="Adresse A")
        # Créer un produit et deux stocks pour ce produit
        self.produit = Produit.objects.create(nom="Produit A", categorie="Catégorie", prix=10.00)
        Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=4)   # rupture_stock car <=5
        Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=120) # surstock car >=100

        # Créer une vente récente
        vente = Vente.objects.create(magasin=self.magasin)
        LigneVente.objects.create(vente=vente, produit=self.produit, quantite=5, prix_unitaire=10.00)
        # Créer une vente plus ancienne pour ne pas figurer dans la tendance
        old_date = datetime.datetime.now() - datetime.timedelta(days=10)
        vente_old = Vente.objects.create(magasin=self.magasin)
        vente_old.date = old_date
        vente_old.save()
        LigneVente.objects.create(vente=vente_old, produit=self.produit, quantite=2, prix_unitaire=10.00)

    def test_tableau_bord_view(self):
        """
        Vérifie que la vue 'tableau_bord' renvoie le status code 200, le template 'tableau_de_bord.html'
        et que le contexte contient les clés 'chiffre_affaires', 'ruptures_stock', 'surstock' et 'tendances'.
        """
        url = reverse('tableau_bord')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tableau_de_bord.html')
        self.assertIn('chiffre_affaires', response.context)
        self.assertIn('ruptures_stock', response.context)
        self.assertIn('surstock', response.context)
        self.assertIn('tendances', response.context)

class DemandeReapproUtilisateurViewTests(TestCase):
    """
    Tests unitaires pour la vue 'demande_reappro_utilisateur' qui gère
    l'interface de demande de réapprovisionnement pour un employé.
    """

    def setUp(self):
        """
        Initialise l'environnement de test en créant un magasin local, un magasin central,
        un produit et les stocks associés pour tester la vue.
        """
        self.magasin_local = Magasin.objects.create(nom="Magasin Local", adresse="Adresse Loc")
        self.magasin_central = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Adresse Centre")
        self.produit = Produit.objects.create(nom="Produit Test", categorie="Catégorie", prix=10.00)
        self.stock_local = Stock.objects.create(magasin=self.magasin_local, produit=self.produit, quantite=5)
        self.stock_central = Stock.objects.create(magasin=self.magasin_central, produit=self.produit, quantite=20)

    def test_demande_reappro_utilisateur_get(self):
        """
        Vérifie que la vue 'demande_reappro_utilisateur' renvoie un status code 200 et utilise
        le template approprié.
        """
        url = reverse("demande_reappro_utilisateur", args=[self.stock_local.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "demande_reappro_utilisateur.html")


class TraiterDemandeReapproViewTests(TestCase):
    """
    Tests unitaires pour la vue 'traiter_demande_reappro' qui traite les demandes de réapprovisionnement.
    """

    def setUp(self):
        """
        Initialise l'environnement de test en créant un centre logistique, un magasin local,
        un produit, un stock pour le centre et une demande de réapprovisionnement.
        """
        self.centre = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Adresse Centre")
        self.magasin_local = Magasin.objects.create(nom="Magasin Local", adresse="Adresse Loc")
        self.produit = Produit.objects.create(nom="Produit Test", categorie="Catégorie", prix=10.00)
        self.stock_centre = Stock.objects.create(magasin=self.centre, produit=self.produit, quantite=10)
        # Créer une demande de réapprovisionnement
        self.demande = DemandeReappro.objects.create(
            magasin=self.magasin_local,
            produit=self.produit,
            quantite=5,
            statut='pending'
        )

    def test_traiter_demande_approve_success(self):
        """
        Vérifie que l'approbation d'une demande de réapprovisionnement fonctionne :
        la demande est approuvée, la date de traitement est définie, et le stock du centre est décrémenté.
        """
        url = reverse("traiter_demande_reappro")
        data = {"demande_id": self.demande.id, "action": "approve"}
        response = self.client.post(url, data)
        self.demande.refresh_from_db()
        self.stock_centre.refresh_from_db()
        self.assertEqual(self.demande.statut, "approved")
        self.assertIsNotNone(self.demande.date_traitement)
        self.assertEqual(self.stock_centre.quantite, 10 - self.demande.quantite)
        # Vérifier que le stock local a été mis à jour (création automatique si nécessaire)
        stock_local = Stock.objects.get(magasin=self.magasin_local, produit=self.produit)
        self.assertEqual(stock_local.quantite, self.demande.quantite)

    def test_traiter_demande_approve_insufficient_stock(self):
        """
        Vérifie que si la demande dépasse le stock disponible, la demande est refusée.
        """
        # Définir une quantité trop élevée
        self.demande.quantite = 20
        self.demande.save()
        url = reverse("traiter_demande_reappro")
        data = {"demande_id": self.demande.id, "action": "approve"}
        response = self.client.post(url, data)
        self.demande.refresh_from_db()
        # On s'attend à ce que la demande soit refusée à cause du stock insuffisant
        self.assertEqual(self.demande.statut, "refused")

    def test_traiter_demande_refuse(self):
        """
        Vérifie que l'action 'refuse' met à jour la demande avec le statut 'refused' et définit la date de traitement.
        """
        url = reverse("traiter_demande_reappro")
        data = {"demande_id": self.demande.id, "action": "refuse"}
        response = self.client.post(url, data)
        self.demande.refresh_from_db()
        self.assertEqual(self.demande.statut, "refused")
        self.assertIsNotNone(self.demande.date_traitement)


class ModifierProduitViewTests(TestCase):
    """
    Tests unitaires pour la vue 'modifier_produit' qui permet de modifier les informations d'un produit.
    """

    def setUp(self):
        """
        Initialise l'environnement de test en créant un produit dont les détails pourront être modifiés.
        """
        self.produit = Produit.objects.create(nom="Ancien Nom", categorie="Old Cat", prix=Decimal("10.00"))

    def test_modifier_produit_get(self):
        """
        Vérifie que la requête GET de la vue 'modifier_produit' renvoie le status 200 et le bon template,
        et que le contexte contient la clé 'product'.
        """
        url = reverse("modifier_produit", args=[self.produit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "modifier_produit.html")
        self.assertIn("product", response.context)

    def test_modifier_produit_post_missing_name(self):
        """
        Vérifie que la soumission d'un formulaire sans nom de produit renvoie un message d'erreur approprié.
        """
        url = reverse("modifier_produit", args=[self.produit.id])
        data = {"nom": "", "categorie": "Nouvelle Cat", "prix": "15.00"}
        response = self.client.post(url, data)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Le nom du produit est requis." in m.message for m in messages_list))

    def test_modifier_produit_post_invalid_price(self):
        """
        Vérifie que la soumission d'un formulaire avec un prix invalide renvoie un message d'erreur approprié.
        """
        url = reverse("modifier_produit", args=[self.produit.id])
        data = {"nom": "Nouveau Nom", "categorie": "Nouvelle Cat", "prix": "abc"}
        response = self.client.post(url, data)
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Veuillez entrer un prix valide." in m.message for m in messages_list))

    def test_modifier_produit_post_success(self):
        """
        Vérifie qu'une modification réussie met à jour les informations du produit et affiche un message de succès.
        """
        url = reverse("modifier_produit", args=[self.produit.id])
        data = {"nom": "Nouveau Nom", "categorie": "Nouvelle Cat", "prix": "20.00"}
        response = self.client.post(url, data)
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.nom, "Nouveau Nom")
        self.assertEqual(self.produit.categorie, "Nouvelle Cat")
        self.assertEqual(self.produit.prix, Decimal("20.00"))
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Produit mis à jour avec succès" in m.message for m in messages_list))


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