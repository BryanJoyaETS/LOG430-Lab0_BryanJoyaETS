from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from .models import Magasin, Produit, Vente, LigneVente, Stock, DemandeReappro
import datetime
from django.db.models import Sum
from django.contrib.messages import get_messages

## Tests unitaire pour les modèles
class MagasinModelTests(TestCase):
    def test_str_returns_nom(self):
        magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.assertEqual(str(magasin), "Magasin Test")


class ProduitModelTests(TestCase):
    def test_str_returns_nom(self):
        produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        self.assertEqual(str(produit), "Produit X")


class VenteModelTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
    
    def test_str_contains_vente_and_date(self):
        vente = Vente.objects.create(magasin=self.magasin)
        self.assertIn("Vente", str(vente))
    
    def test_default_est_retournee(self):
        vente = Vente.objects.create(magasin=self.magasin)
        self.assertFalse(vente.est_retournee)  


class LigneVenteTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        self.vente = Vente.objects.create(magasin=self.magasin)
    
    def test_str_returns_ligne_details(self):
        ligne = LigneVente.objects.create(
            vente=self.vente,
            produit=self.produit,
            quantite=2,
            prix_unitaire=25.00
        )
        expected_str = "2 x Produit X at 25.00"
        self.assertEqual(str(ligne), expected_str)


class StockModelTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
    
    def test_str_returns_stock_details(self):
        stock = Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)
        expected_str = "10 of Produit X in Magasin Test"
        self.assertEqual(str(stock), expected_str)
    
    def test_negative_quantite_not_allowed(self):
        stock = Stock(magasin=self.magasin, produit=self.produit, quantite=-5)
        with self.assertRaises(ValidationError):
            stock.clean()


class DemandeReapproModelTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue de Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
    
    def test_default_statut_is_pending(self):
        demande = DemandeReappro.objects.create(magasin=self.magasin, produit=self.produit, quantite=50)
        self.assertEqual(demande.statut, "pending")
    
    def test_str_returns_correct_information(self):
        demande = DemandeReappro.objects.create(magasin=self.magasin, produit=self.produit, quantite=50)
        expected_str = f"50 x Produit X pour Magasin Test (En attente)"
        self.assertEqual(str(demande), expected_str)

#Tests unitaires pour les vues

class AfficherMagasinsViewTests(TestCase):
    def setUp(self):
        # Créer plus de 10 magasins pour tester la pagination.
        for i in range(15):
            Magasin.objects.create(nom=f"Magasin {i}", adresse="123 Rue Test")

    def test_afficher_magasins_status_et_template(self):
        response = self.client.get(reverse('index'))  # Assurez-vous de définir le nom 'afficher_magasins' dans urls.py.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        # Vérifier que nous avons bien 10 éléments sur la première page
        self.assertEqual(len(response.context['magasins']), 10)



class InterfaceCaisseViewTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")

    def test_interface_caisse_existant(self):
        response = self.client.get(reverse('menu_caisse', args=[self.magasin.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu_caisse.html')
        self.assertEqual(response.context['magasin'], self.magasin)

    def test_interface_caisse_inexistant(self):
        # Utilisation d'un identifiant inexistant devrait renvoyer un 404.
        response = self.client.get(reverse('menu_caisse', args=[9999]))
        self.assertEqual(response.status_code, 404)


class RechercheProduitViewTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        # Création du stock lié à ce produit dans le magasin
        Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)

    def test_recherche_get(self):
        # Vérification pour une requête GET
        response = self.client.get(reverse('recherche_produit', args=[self.magasin.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recherche.html')

    def test_recherche_post_sans_critere(self):
        response = self.client.post(reverse('recherche_produit', args=[self.magasin.id]), {})
        self.assertContains(response, "Veuillez remplir au moins un critère.")

    def test_recherche_post_identifiant_invalide(self):
        data = {'identifiant': 'abc'}
        response = self.client.post(reverse('recherche_produit', args=[self.magasin.id]), data)
        self.assertContains(response, "Identifiant invalide.")

    def test_recherche_post_produit_trouve(self):
        data = {'nom': 'Produit'}
        response = self.client.post(reverse('recherche_produit', args=[self.magasin.id]), data)
        # Le résultat doit contenir le produit recherché
        self.assertIsNotNone(response.context['resultats'])
        results = response.context['resultats']
        self.assertTrue(results.exists())
        self.assertIsNone(response.context['message_erreur'])

class EnregistrerVenteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        self.produit = Produit.objects.create(nom="Produit X", categorie="Catégorie A", prix=25.00)
        self.stock = Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)

    def test_vente_quantite_negative(self):
        data = {'produit_id': str(self.produit.id), 'quantite': '-3'}
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        self.assertContains(response, "La quantité doit être positive.")

    def test_vente_produit_non_trouve_dans_magasin(self):
        # Utiliser un produit_id qui n'existe pas dans le stock du magasin
        data = {'produit_id': '9999', 'quantite': '1'}
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        self.assertContains(response, "Produit introuvable dans ce magasin.")

    def test_vente_stock_insuffisant(self):
        data = {'produit_id': str(self.produit.id), 'quantite': '20'}  # Plus que disponible
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        self.assertContains(response, "Stock insuffisant pour cette vente.")

    def test_vente_success(self):
        quantite = 3
        data = {'produit_id': str(self.produit.id), 'quantite': str(quantite)}
        response = self.client.post(reverse('enregistrer_vente', args=[self.magasin.id]), data)
        # Vérifier le message de succès
        expected_message = f"Vente enregistrée : {quantite} x {self.produit.nom}."
        self.assertContains(response, expected_message)
        
        # Vérifier que la vente et la ligne de vente ont bien été créées
        self.assertTrue(Vente.objects.filter(magasin=self.magasin).exists())
        self.assertTrue(LigneVente.objects.filter(vente__magasin=self.magasin, produit=self.produit).exists())
        
        # Vérifier que le stock a été décrémenté
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantite, 10 - quantite)

class TraiterRetourViewTests(TestCase):
    def setUp(self):
        # Créer un magasin
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        # Créer un produit
        self.produit = Produit.objects.create(nom="Produit A", categorie="Catégorie A", prix=25.00)
        # Créer un stock pour le produit dans ce magasin
        self.stock = Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=10)
        # Créer une vente avec une ligne de vente
        self.vente = Vente.objects.create(magasin=self.magasin)
        self.ligne = LigneVente.objects.create(
            vente=self.vente,
            produit=self.produit,
            quantite=2,
            prix_unitaire=self.produit.prix
        )

    def test_get_method(self):
        url = reverse('traiter_retour', args=[self.magasin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "retour.html")
        # Par défaut, le message est None ou vide dans le contexte.
        self.assertIn("message", response.context)

    def test_post_with_invalid_vente_id(self):
        url = reverse('traiter_retour', args=[self.magasin.id])
        response = self.client.post(url, {"vente_id": "abc"})
        self.assertContains(response, "ID de vente invalide.")

    def test_post_with_nonexistent_vente(self):
        url = reverse('traiter_retour', args=[self.magasin.id])
        response = self.client.post(url, {"vente_id": 9999})
        self.assertContains(response, "Vente introuvable dans ce magasin.")

    def test_traiter_retour_success(self):
        url = reverse('traiter_retour', args=[self.magasin.id])
        initial_stock = self.stock.quantite
        data = {"vente_id": self.vente.id}
        response = self.client.post(url, data)
        # Vérifier le message de succès
        expected_message = f"Retour traité : la vente {self.vente.id} a été annulée et le stock mis à jour."
        self.assertContains(response, expected_message)
        # La vente doit être supprimée
        with self.assertRaises(Vente.DoesNotExist):
            Vente.objects.get(id=self.vente.id)
        # Le stock doit être incrémenté de la quantité vendue de la ligne
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantite, initial_stock + self.ligne.quantite)

class StockMagasinViewTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        # Créer plusieurs stocks
        self.produit1 = Produit.objects.create(nom="Produit A", categorie="Catégorie", prix=25.00)
        self.produit2 = Produit.objects.create(nom="Produit B", categorie="Catégorie", prix=30.00)
        Stock.objects.create(magasin=self.magasin, produit=self.produit1, quantite=5)
        Stock.objects.create(magasin=self.magasin, produit=self.produit2, quantite=15)

    def test_stock_magasin_view(self):
        url = reverse('stock_magasin', args=[self.magasin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stock_magasin.html')
        # Vérifier que le contexte contient bien la liste de stocks
        self.assertIn('stocks', response.context)
        self.assertEqual(response.context['magasin'], self.magasin)
        self.assertEqual(response.context['stocks'].count(), 2)

class HistoriqueTransactionsViewTests(TestCase):
    def setUp(self):
        self.magasin = Magasin.objects.create(nom="Magasin Test", adresse="123 Rue Test")
        # Créer quelques ventes et lignes associées
        self.vente1 = Vente.objects.create(magasin=self.magasin)
        self.vente2 = Vente.objects.create(magasin=self.magasin)
        self.produit = Produit.objects.create(nom="Produit A", categorie="Catégorie", prix=25.00)
        LigneVente.objects.create(vente=self.vente1, produit=self.produit, quantite=2, prix_unitaire=25.00)
        LigneVente.objects.create(vente=self.vente2, produit=self.produit, quantite=3, prix_unitaire=25.00)

    def test_historique_transactions_view(self):
        url = reverse('historique_transactions', args=[self.magasin.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'historique.html')
        self.assertEqual(response.context['magasin'], self.magasin)
        # Vérifiez que les ventes sont ordonnées par date décroissante
        ventes = list(response.context['ventes'])
        self.assertGreaterEqual(ventes[0].date, ventes[1].date)

class GenererRapportViewTests(TestCase):
    def setUp(self):
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
        url = reverse('generer_rapport')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rapport_de_ventes.html')
        self.assertIn('ventes_par_magasin', response.context)
        self.assertIn('produits_populaires', response.context)
        self.assertIn('stock_restant', response.context)


class TableauBordViewTests(TestCase):
    def setUp(self):
        # Créer le centre logistique et d'autres magasins
        self.centre = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Adresse Centre")
        self.magasin = Magasin.objects.create(nom="Magasin A", adresse="Adresse A")
        # Créer un produit et stock
        self.produit = Produit.objects.create(nom="Produit A", categorie="Catégorie", prix=10.00)
        Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=4)   # rupture_stock car <=5
        Stock.objects.create(magasin=self.magasin, produit=self.produit, quantite=120) # surstock car >=100
        
        # Créer des ventes récentes
        vente = Vente.objects.create(magasin=self.magasin)
        LigneVente.objects.create(vente=vente, produit=self.produit, quantite=5, prix_unitaire=10.00)
        # Créer une vente moins récente pour ne pas figurer dans la tendance
        old_date = datetime.datetime.now() - datetime.timedelta(days=10)
        vente_old = Vente.objects.create(magasin=self.magasin)
        vente_old.date = old_date
        vente_old.save()
        LigneVente.objects.create(vente=vente_old, produit=self.produit, quantite=2, prix_unitaire=10.00)

    def test_tableau_bord_view(self):
        url = reverse('tableau_bord')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tableau_de_bord.html')
        self.assertIn('chiffre_affaires', response.context)
        self.assertIn('ruptures_stock', response.context)
        self.assertIn('surstock', response.context)
        self.assertIn('tendances', response.context)


class DemandeReapproUtilisateurViewTests(TestCase):
    def setUp(self):
        self.magasin_local = Magasin.objects.create(nom="Magasin Local", adresse="Adresse Loc")
        self.magasin_central = Magasin.objects.create(nom="CENTRE_LOGISTIQUE", adresse="Adresse Centre")
        self.produit = Produit.objects.create(nom="Produit Test", categorie="Catégorie", prix=10.00)
        self.stock_local = Stock.objects.create(magasin=self.magasin_local, produit=self.produit, quantite=5)
        self.stock_central = Stock.objects.create(magasin=self.magasin_central, produit=self.produit, quantite=20)

    def test_demande_reappro_utilisateur_get(self):
        url = reverse("demande_reappro_utilisateur", args=[self.stock_local.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "demande_reappro_utilisateur.html")

class TraiterDemandeReapproViewTests(TestCase):
    def setUp(self):
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
        url = reverse("traiter_demande_reappro")
        data = {"demande_id": self.demande.id, "action": "approve"}
        response = self.client.post(url, data)
        self.demande.refresh_from_db()
        self.stock_centre.refresh_from_db()
        # La demande doit être approuvée et la demande de stock effectif réalisée
        self.assertEqual(self.demande.statut, "approved")
        self.assertIsNotNone(self.demande.date_traitement)
        self.assertEqual(self.stock_centre.quantite, 10 - self.demande.quantite)
        # Vérifier que le stock local a été mis à jour (création automatique si nécessaire)
        stock_local = Stock.objects.get(magasin=self.magasin_local, produit=self.produit)
        self.assertEqual(stock_local.quantite, self.demande.quantite)

    def test_traiter_demande_approve_insufficient_stock(self):
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
        url = reverse("traiter_demande_reappro")
        data = {"demande_id": self.demande.id, "action": "refuse"}
        response = self.client.post(url, data)
        self.demande.refresh_from_db()
        self.assertEqual(self.demande.statut, "refused")
        self.assertIsNotNone(self.demande.date_traitement)

class ModifierProduitViewTests(TestCase):
    def setUp(self):
        self.produit = Produit.objects.create(nom="Ancien Nom", categorie="Old Cat", prix=Decimal("10.00"))

    def test_modifier_produit_get(self):
        url = reverse("modifier_produit", args=[self.produit.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "modifier_produit.html")
        self.assertIn("product", response.context)

    def test_modifier_produit_post_missing_name(self):
        url = reverse("modifier_produit", args=[self.produit.id])
        data = {"nom": "", "categorie": "Nouvelle Cat", "prix": "15.00"}
        response = self.client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Le nom du produit est requis." in m.message for m in messages))

    def test_modifier_produit_post_invalid_price(self):
        url = reverse("modifier_produit", args=[self.produit.id])
        data = {"nom": "Nouveau Nom", "categorie": "Nouvelle Cat", "prix": "abc"}
        response = self.client.post(url, data)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Veuillez entrer un prix valide." in m.message for m in messages))

    def test_modifier_produit_post_success(self):
        url = reverse("modifier_produit", args=[self.produit.id])
        data = {"nom": "Nouveau Nom", "categorie": "Nouvelle Cat", "prix": "20.00"}
        response = self.client.post(url, data)
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.nom, "Nouveau Nom")
        self.assertEqual(self.produit.categorie, "Nouvelle Cat")
        self.assertEqual(self.produit.prix, Decimal("20.00"))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Produit mis à jour avec succès" in m.message for m in messages))

class ListeProduitsViewTests(TestCase):
    def setUp(self):
        Produit.objects.create(nom="Produit C", categorie="Cat", prix=30.00)
        Produit.objects.create(nom="Produit A", categorie="Cat", prix=10.00)
        Produit.objects.create(nom="Produit B", categorie="Cat", prix=20.00)

    def test_liste_produits_view(self):
        url = reverse("liste_produits")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "liste_produits.html")
        produits = response.context["produits"]
        # Vérifier l'ordre par nom
        noms = [p.nom for p in produits]
        self.assertEqual(noms, sorted(noms))