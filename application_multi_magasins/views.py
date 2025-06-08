"""
Module de vues de l'application application_multi_magasins.
"""
# pylint: disable=no-member
from django.db import DatabaseError,transaction
from django.shortcuts import get_object_or_404, render, redirect

from application_multi_magasins.business.magasin_service import get_paginated_magasins

from .models import Magasin, Stock, Vente, LigneVente

def afficher_magasins(request):
    """UC0 – Page d’accueil : liste paginée des magasins."""
    magasins = get_paginated_magasins(request)
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


















