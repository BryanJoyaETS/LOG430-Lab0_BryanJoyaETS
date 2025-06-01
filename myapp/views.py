# myapp/views.py
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from .models import LigneVente, Magasin, Produit, Stock, Vente  # and import other needed models or logic
from django.core.paginator import Paginator
from django.db.models import Sum

def recherche_produit(request):
    result = None
    if request.method == "POST":
        identifiant = request.POST.get('identifiant')
        nom = request.POST.get('nom')
        categorie = request.POST.get('categorie')
        
        # Convert identifiant to int if provided.
        try:
            identifiant = int(identifiant) if identifiant else None
        except ValueError:
            result = "Identifiant invalide."
        else:
            # Here you would implement the search logic.
            query = {}
            if identifiant is not None:
                query['id'] = identifiant
            if nom:
                query['nom__icontains'] = nom
            if categorie:
                query['categorie__icontains'] = categorie

            if query:
                produits = Produit.objects.filter(**query)
                if produits.exists():
                    result = produits


            if not result:
                result = "Aucun produit trouvé."
    return render(request, 'recherche.html', {'result': result})

def enregistrer_vente(request):
    message = ""
    if request.method == "POST":
        # Here you would process the sale.
        # For example, you might extract a list of products and their quantities:
        produits = []
        # (A more complex implementation may involve dynamic forms or JavaScript.)
        produit_id = request.POST.get('produit_id')
        quantite = request.POST.get('quantite')
        try:
            produit_id = int(produit_id)
            quantite = int(quantite)
            # Call your function to record the sale.
            # caisse.enregistrer_vente([(produit_id, quantite)])
            message = "Vente enregistrée avec succès."
        except ValueError:
            message = "Entrée invalide, veuillez saisir des entiers."
    return render(request, 'vente.html', {'message': message})

def traiter_retour(request):
    message = ""
    if request.method == "POST":
        vente_id = request.POST.get('vente_id')
        try:
            vente_id = int(vente_id)
            # Call your logic to process the return.
            # caisse.gerer_retour(vente_id)
            message = "Retour traité avec succès."
        except ValueError:
            message = "ID de vente invalide."
    return render(request, 'retour.html', {'message': message})

def consulter_stock(request):
    produits = Produit.objects.all()  # Récupère tous les produits
    return render(request, 'stock.html', {'produits': produits})

def historique_transactions(request):
    # Récupère toutes les ventes triées par date décroissante
    ventes = Vente.objects.order_by('-date').prefetch_related('lignes')
    return render(request, 'historique.html', {'ventes': ventes})

def afficher_magasins(request):
    magasins_list = Magasin.objects.all()
    paginator = Paginator(magasins_list, 10)  # Affiche 10 magasins par page
    page_number = request.GET.get('page')
    magasins = paginator.get_page(page_number)
    return render(request, 'index.html', {'magasins': magasins})

def stock_magasin(request, magasin_id):
    magasin = get_object_or_404(Magasin, id=magasin_id)  # Vérifie que le magasin existe
    stocks = Stock.objects.filter(magasin=magasin)  # Filtre le stock du magasin
    return render(request, 'stock_magasin.html', {'magasin': magasin, 'stocks': stocks})

def generer_rapport(request):
    # Chiffre d’affaires par magasin
    ventes_par_magasin = Vente.objects.values('magasin__nom').annotate(chiffre_affaires=Sum('lignes__quantite') * Sum('lignes__prix_unitaire'))

    # Produits les plus vendus
    produits_populaires = LigneVente.objects.values('produit__nom').annotate(total_vendu=Sum('quantite')).order_by('-total_vendu')[:5]

    # Stocks restants par magasin
    stock_restant = Stock.objects.values('magasin__nom', 'produit__nom', 'quantite')

    return render(request, 'rapport_de_ventes.html', {
        'ventes_par_magasin': ventes_par_magasin,
        'produits_populaires': produits_populaires,
        'stock_restant': stock_restant
    })


def tableau_bord(request):
    # Chiffre d’affaires par magasin
    chiffre_affaires = Vente.objects.values('magasin__nom').annotate(total=Sum('lignes__quantite') * Sum('lignes__prix_unitaire'))

    # Produits en rupture de stock
    ruptures_stock = Stock.objects.filter(quantite__lte=5).values('magasin__nom', 'produit__nom', 'quantite')

    # Produits en surstock (quantité > 100)
    surstock = Stock.objects.filter(quantite__gte=100).values('magasin__nom', 'produit__nom', 'quantite')

    # Tendances hebdomadaires
    semaine_derniere = datetime.datetime.now() - datetime.timedelta(days=7)
    tendances = Vente.objects.filter(date__gte=semaine_derniere).values('magasin__nom').annotate(total_ventes=Sum('lignes__quantite'))

    return render(request, 'tableau_de_bord.html', {
        'chiffre_affaires': chiffre_affaires,
        'ruptures_stock': ruptures_stock,
        'surstock': surstock,
        'tendances': tendances
    })
