# myapp/views.py
from django.shortcuts import render, redirect
from .models import Produit, Vente  # and import other needed models or logic

def index(request):
    # This view simply renders the main menu page.
    return render(request, 'index.html')

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
