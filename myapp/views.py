# myapp/views.py
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Magasin, Produit, Stock, Vente, LigneVente
from django.db import transaction
# si vous avez des forms, importez-les ici
# from .forms import DemandeReapproForm, VenteForm, RetourForm

def afficher_magasins(request):
    """UC0 – Page d’accueil : liste paginée des magasins."""
    magasins_list = Magasin.objects.all()
    paginator     = Paginator(magasins_list, 10)  # 10 par page
    page_number   = request.GET.get('page')
    magasins      = paginator.get_page(page_number)
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
                qs = Stock.objects.filter(magasin=magasin, **filtres)
                if qs.exists():
                    resultats = qs
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
   # views.py
    """
    Enregistre une vente depuis la caisse du magasin.
    """
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
    Traite un retour en annulant une vente.
    L'utilisateur saisit l'ID d'une vente. Pour chaque ligne de cette vente,
    le nombre de produits vendus est réintégré dans le stock du magasin.
    La vente est marquée comme retournée pour éviter un double traitement.
    """
    magasin = get_object_or_404(Magasin, id=magasin_id)
    message = ""

    if request.method == "POST":
        vente_id_input = request.POST.get("vente_id", "").strip()
        
        try:
            vente_id = int(vente_id_input)
        except ValueError:
            message = "ID de vente invalide."
        else:
            try:
                vente = Vente.objects.get(id=vente_id)
            except Vente.DoesNotExist:
                message = "Vente introuvable."
            else:
                if vente.magasin.id != magasin.id:
                    message = "La vente ne correspond pas à ce magasin."
                elif vente.est_retournee:
                    message = "Ce retour a déjà été traité pour cette vente."
                else:
                    with transaction.atomic():
                        # Pour chaque ligne de vente, mettre à jour le stock.
                        for ligne in vente.lignes.all():
                            try:
                                stock = Stock.objects.get(magasin=magasin, produit=ligne.produit)
                            except Stock.DoesNotExist:
                                # Si aucun stock n'existe pour le produit, vous pouvez décider de l'ignorer
                                # ou de créer un nouvel enregistrement.
                                continue
                            
                            stock.quantite += ligne.quantite
                            stock.save()
                        
                        # Marquer la vente comme retournée
                        vente.est_retournee = True
                        vente.save()
                        
                        message = f"Retour traité pour la vente {vente.id}."

    return render(request, "retour.html", {"magasin": magasin, "message": message})



def stock_magasin(request, magasin_id):
    """UC2.4 – Consulter le stock d’un magasin (pour la caisse)."""
    magasin = get_object_or_404(Magasin, id=magasin_id)
    stocks  = Stock.objects.filter(magasin=magasin)
    return render(request, 'stock_magasin.html', {
        'magasin': magasin,
        'stocks':  stocks
    })


def historique_transactions(request, magasin_id):
    """UC2.5 – Historique des transactions d’un magasin."""
    magasin      = get_object_or_404(Magasin, id=magasin_id)
    ventes       = (Vente.objects
                    .filter(magasin=magasin)
                    .order_by('-date')
                    .prefetch_related('lignes'))
    return render(request, 'historique.html', {
        'magasin':    magasin,
        'ventes':     ventes
    })


def generer_rapport(request):
    """UC1 – Rapport consolidé des ventes (maison mère)."""
    ventes_par_magasin = (Vente.objects
                          .values('magasin__nom')
                          .annotate(
                            chiffre_affaires=Sum('lignes__quantite')
                                            * Sum('lignes__prix_unitaire')
                          ))
    produits_populaires= (LigneVente.objects
                          .values('produit__nom')
                          .annotate(total_vendu=Sum('quantite'))
                          .order_by('-total_vendu')[:5])
    stock_restant     = Stock.objects.values(
                          'magasin__nom', 'produit__nom', 'quantite')

    return render(request, 'rapport_de_ventes.html', {
        'ventes_par_magasin':  ventes_par_magasin,
        'produits_populaires': produits_populaires,
        'stock_restant':       stock_restant
    })


def tableau_bord(request):
    """UC3 – Tableau de bord synthétique (maison mère)."""
    chiffre_affaires = (Vente.objects
                        .values('magasin__nom')
                        .annotate(
                          total=Sum('lignes__quantite')
                                * Sum('lignes__prix_unitaire')
                        ))
    ruptures_stock   = Stock.objects.filter(quantite__lte=5).values(
                          'magasin__nom', 'produit__nom', 'quantite')
    surstock         = Stock.objects.filter(quantite__gte=100).values(
                          'magasin__nom', 'produit__nom', 'quantite')
    semaine_derniere = datetime.datetime.now() - datetime.timedelta(days=7)
    tendances        = (Vente.objects
                        .filter(date__gte=semaine_derniere)
                        .values('magasin__nom')
                        .annotate(total_ventes=Sum('lignes__quantite')))

    return render(request, 'tableau_de_bord.html', {
        'chiffre_affaires': chiffre_affaires,
        'ruptures_stock':   ruptures_stock,
        'surstock':         surstock,
        'tendances':        tendances
    })


def demande_reappro(request, stock_id):
    """UC4 – Demande de réapprovisionnement."""
    stock = get_object_or_404(Stock, id=stock_id)
    stock.quantite += 0  # si vous gérez directement ici
    stock.save()        #
