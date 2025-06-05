"""
Module de vues de l'application myapp.
"""
# pylint: disable=no-member
import datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import DatabaseError,transaction
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .models import DemandeReappro, Magasin, Produit, Stock, Vente, LigneVente

def afficher_magasins(request):
    """UC0 – Page d’accueil : liste paginée des magasins."""
    magasins_list = Magasin.objects.all()
    paginator = Paginator(magasins_list, 10)
    page_number = request.GET.get('page')
    magasins = paginator.get_page(page_number)
    return render(request, 'index.html', {'magasins': magasins})

def interface_caisse(request, magasin_id):
    """UC2 – Menu de la caisse pour un magasin donné."""
    magasin = get_object_or_404(Magasin, id=magasin_id)
    return render(request, 'menu_caisse.html', {'magasin': magasin})

def recherche_produit(request, magasin_id):
    """UC2.1 – Recherche produit (POST) pour la caisse."""
    magasin = get_object_or_404(Magasin, id=magasin_id)
    resultats = None
    message_erreur = None

    if request.method == "POST":
        identifiant = request.POST.get('identifiant')
        nom = request.POST.get('nom')
        categorie = request.POST.get('categorie')

        # Validation de l’ID
        try:
            identifiant = int(identifiant) if identifiant else None
        except ValueError:
            message_erreur = "Identifiant invalide."

        if not message_erreur:
            filtres = {}
            if identifiant is not None:
                filtres['produit__id'] = identifiant
            if nom:
                filtres['produit__nom__icontains'] = nom
            if categorie:
                filtres['produit__categorie__icontains'] = categorie

            if filtres:
                # On recherche parmi les stocks du magasin
                queryset = Stock.objects.filter(magasin=magasin, **filtres)
                if queryset.exists():
                    resultats = queryset
                else:
                    message_erreur = "Aucun produit trouvé."
            else:
                message_erreur = "Veuillez remplir au moins un critère."

    return render(request, 'recherche.html', {
        'magasin': magasin,
        'resultats': resultats,
        'message_erreur': message_erreur
    })

def enregistrer_vente(request, magasin_id):
    """UC2.2 – Enregistrer une vente pour la caisse."""
    magasin = get_object_or_404(Magasin, id=magasin_id)
    message = None

    if request.method == "POST":
        produit_id = request.POST.get('produit_id')
        quantite = request.POST.get('quantite')

        # Conversion et validation des données
        try:
            produit_id = int(produit_id)
            quantite = int(quantite)
        except (TypeError, ValueError):
            message = "Les données saisies sont invalides."
        else:
            if quantite <= 0:
                message = "La quantité doit être positive."

        if not message:
            try:
                # Recherche le stock correspondant à ce produit dans ce magasin.
                stock = Stock.objects.get(magasin=magasin, produit__id=produit_id)
            except Stock.DoesNotExist:
                message = "Produit introuvable dans ce magasin."
            else:
                if stock.quantite < quantite:
                    message = "Stock insuffisant pour cette vente."
                else:
                    # Utiliser une transaction pour garantir une mise à jour cohérente.
                    with transaction.atomic():
                        # Création de la vente.
                        vente = Vente.objects.create(magasin=magasin)
                        # Création de la ou des lignes de vente.
                        LigneVente.objects.create(
                            vente=vente,
                            produit=stock.produit,
                            quantite=quantite,
                            prix_unitaire=stock.produit.prix
                        )
                        # Mise à jour du stock.
                        stock.quantite -= quantite
                        stock.save()

                    message = f"Vente enregistrée : {quantite} x {stock.produit.nom}."

    return render(request, "vente.html", {
        "magasin": magasin,
        "message": message,
    })

def traiter_retour(request, magasin_id):
    """
    Annule une vente en réintégrant les quantités vendues dans le stock 
    et en supprimant la vente (ainsi que ses lignes associées, grâce au CASCADE).
    """
    magasin = get_object_or_404(Magasin, id=magasin_id)
    message = None

    if request.method == "POST":
        vente_id_input = request.POST.get("vente_id", "").strip()

        # Conversion de l'ID de vente
        try:
            vente_id = int(vente_id_input)
        except ValueError:
            message = "ID de vente invalide."
        else:
            try:
                # On vérifie que la vente existe et qu'elle appartient au magasin courant
                vente = Vente.objects.get(id=vente_id, magasin=magasin)
            except Vente.DoesNotExist:
                message = "Vente introuvable dans ce magasin."
            else:
                # Procéder au retour dans une transaction atomique
                try:
                    with transaction.atomic():
                        # Pour chaque ligne de vente, on augmente le stock du produit
                        for ligne in vente.lignes.all():
                            stock, _ = Stock.objects.get_or_create(
                                magasin=magasin,
                                produit=ligne.produit,
                                defaults={"quantite": 0}
                            )
                            stock.quantite += ligne.quantite
                            stock.save()

                        # Supprimer la vente (les lignes associées sont supprimées en cascade)
                        vente.delete()

                    message = (
                        f"Retour traité : la vente {vente_id} a été annulée "
                        "et le stock mis à jour."
                    )
                except DatabaseError as exc:
                    message = f"Erreur lors du traitement du retour: {exc}"

    return render(request, "retour.html", {"magasin": magasin, "message": message})

def stock_magasin(request, magasin_id):
    """UC2.4 – Consulter le stock d’un magasin (pour la caisse)."""
    magasin = get_object_or_404(Magasin, id=magasin_id)
    stocks = Stock.objects.filter(magasin=magasin)
    return render(request, 'stock_magasin.html', {
        'magasin': magasin,
        'stocks': stocks
    })


def historique_transactions(request, magasin_id):
    """UC2.5 – Historique des transactions d’un magasin."""
    magasin = get_object_or_404(Magasin, id=magasin_id)
    ventes = (Vente.objects
              .filter(magasin=magasin)
              .order_by('-date')
              .prefetch_related('lignes'))
    return render(request, 'historique.html', {
        'magasin': magasin,
        'ventes': ventes
    })

def generer_rapport(request):
    """UC1 – Rapport consolidé des ventes (maison mère)."""
    centre = get_object_or_404(Magasin, nom='CENTRE_LOGISTIQUE')

    # Calcul du chiffre d'affaires par magasin (hors centre logistique)
    ventes_par_magasin = (
        Vente.objects.exclude(magasin=centre)
        .values('magasin__nom')
        .annotate(
            chiffre_affaires=Sum(
            ExpressionWrapper(
                F('lignes__quantite') * F('lignes__prix_unitaire'),
                output_field=DecimalField()
                )
            )
        )
        .order_by('magasin__nom')
    )

    # Top 5 des produits les plus vendus
    produits_populaires = (
        LigneVente.objects
        .values('produit__nom')
        .annotate(total_vendu=Sum('quantite'))
        .order_by('-total_vendu')[:5]
    )

    # Stock restant par magasin et produit (hors centre logistique)
    stock_restant = (
        Stock.objects.exclude(magasin=centre)
        .values('magasin__nom', 'produit__nom', 'quantite')
        .order_by('magasin__nom')
    )

    return render(request, 'rapport_de_ventes.html', {
        'ventes_par_magasin': ventes_par_magasin,
        'produits_populaires': produits_populaires,
        'stock_restant': stock_restant
    })


def tableau_bord(request):
    """UC3 – Tableau de bord synthétique (maison mère)."""
    centre = get_object_or_404(Magasin, nom='CENTRE_LOGISTIQUE')

    # Chiffre d'affaires par magasin
    chiffre_affaires = (
        Vente.objects.exclude(magasin=centre)
                     .order_by('magasin__nom')
                     .values('magasin__nom')
                     .annotate(
                         total=Sum(
                             ExpressionWrapper(
                                 F('lignes__quantite') * F('lignes__prix_unitaire'),
                                 output_field=DecimalField()
                             )
                         )
                    )
    )

    # Produits en rupture de stock (<= 5)
    ruptures_stock = (
        Stock.objects.exclude(magasin=centre)
        .filter(quantite__lte=5)
        .values('magasin__nom', 'produit__nom', 'quantite')
    )

    # Produits en surstock (>= 100)
    surstock = (
        Stock.objects.exclude(magasin=centre)
        .filter(quantite__gte=100)
        .values('magasin__nom', 'produit__nom', 'quantite')
    )

    # Tendances de la semaine dernière
    semaine_derniere = timezone.now() - datetime.timedelta(days=7)
    tendances = (
        Vente.objects.exclude(magasin=centre)
        .filter(date__gte=semaine_derniere)
        .values('magasin__nom')
        .annotate(total_ventes=Sum('lignes__quantite'))
    )

    return render(request, 'tableau_de_bord.html', {
        'chiffre_affaires': chiffre_affaires,
        'ruptures_stock': ruptures_stock,
        'surstock': surstock,
        'tendances': tendances
    })

def demande_reappro(request, stock_id):
    """
    Permet le réapprovisionnement d'un produit pour un magasin donné en transférant du stock
    depuis le centre logistique (une instance de Magasin) vers le magasin de l'employé.
    """
    stock_local = get_object_or_404(Stock, id=stock_id)
    magasin_local = stock_local.magasin
    produit = stock_local.produit

    magasin_central = get_object_or_404(Magasin, nom='CENTRE_LOGISTIQUE')
    stock_central = get_object_or_404(Stock, magasin=magasin_central, produit=produit)

    if request.method == "POST":
        qte_str = request.POST.get("quantite", "").strip()
        try:
            quantite = int(qte_str)
        except ValueError:
            messages.error(request, "Veuillez entrer une quantité valide.")
            return redirect("demande_reappro", stock_id=stock_id)

        if quantite <= 0:
            messages.error(request, "La quantité doit être supérieure à zéro.")
            return redirect("demande_reappro", stock_id=stock_id)

        if quantite > stock_central.quantite:
            messages.error(request, "Stock central insuffisant pour ce produit.")
            return redirect("demande_reappro", stock_id=stock_id)

        with transaction.atomic():
            stock_central.quantite -= quantite
            stock_central.save()
            stock_local.quantite += quantite
            stock_local.save()

        messages.success(
            request,
            (
                f"Réapprovisionnement réussi : +{quantite} unité(s) de {produit.nom} "
                f"ajoutées à {magasin_local.nom}."
            )
        )
        return redirect("stock_magasin", magasin_id=magasin_local.id)

    context = {
        "magasin": magasin_local,
        "produit": produit,
        "stock_local": stock_local.quantite,
        "stock_central": stock_central.quantite,
    }
    return render(request, "demande_reappro.html", context)


def demande_reappro_utilisateur(request, stock_id):
    """
    Interface pour l'employé d’un magasin :
    - Affiche le stock local et le stock central (du centre logistique).
    - Permet de saisir une quantité pour créer une demande de réapprovisionnement.
    """
    stock_local = get_object_or_404(Stock, id=stock_id)
    magasin_local = stock_local.magasin
    produit = stock_local.produit

    magasin_central = get_object_or_404(Magasin, nom='CENTRE_LOGISTIQUE')
    stock_central = get_object_or_404(Stock, magasin=magasin_central, produit=produit)

    if request.method == "POST":
        qte_str = request.POST.get("quantite", "").strip()
        try:
            quantite = int(qte_str)
        except ValueError:
            messages.error(request, "Veuillez entrer une quantité valide.")
            return redirect("demande_reappro_utilisateur", stock_id=stock_id)

        if quantite <= 0:
            messages.error(request, "La quantité doit être supérieure à zéro.")
            return redirect("demande_reappro_utilisateur", stock_id=stock_id)

        DemandeReappro.objects.create(
            magasin=magasin_local,
            produit=produit,
            quantite=quantite,
            statut='pending'
        )
        messages.success(request, "Demande de réapprovisionnement envoyée.")
        return redirect("stock_magasin", magasin_id=magasin_local.id)

    context = {
        "magasin": magasin_local,
        "produit": produit,
        "stock_local": stock_local.quantite,
        "stock_central": stock_central.quantite,
    }
    return render(request, "demande_reappro_utilisateur.html", context)


def traiter_demande_reappro(request):
    """
    Interface du responsable logistique pour traiter les demandes de réapprovisionnement.
    Le responsable peut approuver une demande (si le stock central est suffisant)
    ou la refuser. En cas d'approbation, le stock central est décrémenté et le stock
    du magasin demandeur incrémenté, le tout dans une transaction atomique.
    """
    demandes = DemandeReappro.objects.filter(statut='pending').select_related('magasin', 'produit')

    if request.method == "POST":
        demande_id = request.POST.get("demande_id")
        action = request.POST.get("action")
        demande = get_object_or_404(DemandeReappro, id=demande_id, statut='pending')

        centre = get_object_or_404(Magasin, nom="CENTRE_LOGISTIQUE")
        stock_centre = get_object_or_404(Stock, magasin=centre, produit=demande.produit)

        if action == "approve":
            if stock_centre.quantite < demande.quantite:
                messages.error(request, "Stock central insuffisant pour approuver la demande.")
                demande.statut = 'refused'
            else:
                with transaction.atomic():
                    stock_centre.quantite -= demande.quantite
                    stock_centre.save()
                    stock_local, _ = Stock.objects.get_or_create(
                        magasin=demande.magasin,
                        produit=demande.produit,
                        defaults={"quantite": 0}
                    )
                    stock_local.quantite += demande.quantite
                    stock_local.save()
                    demande.statut = 'approved'
            demande.date_traitement = timezone.now()
            demande.save()

        elif action == "refuse":
            demande.statut = 'refused'
            demande.date_traitement = timezone.now()
            demande.save()

        return redirect("traiter_demande_reappro")

    context = {"demandes": demandes}
    return render(request, "traiter_demande_reappro.html", context)


def modifier_produit(request, produit_id):
    """
    Permet au responsable de modifier un produit sans utiliser de Django Form.
    Les nouvelles valeurs sont extraites de request.POST puis appliquées à l'instance Produit.
    """
    produit = get_object_or_404(Produit, id=produit_id)

    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        categorie = request.POST.get("categorie", "").strip()
        prix_str = request.POST.get("prix", "").strip()

        if not nom:
            messages.error(request, "Le nom du produit est requis.")
            return redirect("modifier_produit", produit_id=produit_id)

        try:
            prix = Decimal(prix_str)
        except (InvalidOperation, TypeError):
            messages.error(request, "Veuillez entrer un prix valide.")
            return redirect("modifier_produit", produit_id=produit_id)

        produit.nom = nom
        produit.categorie = categorie
        produit.prix = prix
        produit.save()

        messages.success(
            request,
            (
                "Produit mis à jour avec succès - "
                "les modifications sont synchronisées dans tous les magasins."
            )
        )
        return redirect("liste_produits")

    context = {"product": produit}
    return render(request, "modifier_produit.html", context)


def liste_produits(request):
    """
    Affiche la liste de tous les produits.
    Cette vue récupère tous les objets Produit et les transmet au template.
    """
    produits = Produit.objects.all().order_by('nom')
    return render(request, 'liste_produits.html', {'produits': produits})
