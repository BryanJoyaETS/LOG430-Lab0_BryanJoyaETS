"""
Vues API RESTful

Ce module fournit des vues API RESTful pour la gestion des ressources Vue. Il définit des points de terminaison pour créer, récupérer, mettre à jour et supprimer des objets Vue, en suivant les conventions RESTful. 
L’API prend en charge les méthodes HTTP standard (GET, POST, PUT, DELETE, PATCH) et retourne des réponses au format JSON. 

Points de terminaison :
- GET /vues/ : Lister tous les objets Vue.
- POST /vues/ : Créer un nouvel objet Vue.
- GET /vues/{id}/ : Récupérer un objet Vue spécifique par ID.
- PUT /vues/{id}/ : Mettre à jour un objet Vue spécifique par ID.
- PATCH /vues/{id}/ : Modifier partiellement un objet Vue spécifique par ID.
- DELETE /vues/{id}/ : Supprimer un objet Vue spécifique par ID.

Retourne :
    Réponses JSON avec les codes d’état HTTP appropriés.

Exceptions :
    Http404 : Si l’objet Vue demandé n’existe pas.
    ValidationError : Si les données saisies sont invalides.
    PermissionDenied : Si l’utilisateur n’a pas la permission d’effectuer l’action.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from datetime import timedelta, timezone


from application_multi_magasins.models import (
    Magasin, Produit, Stock, Vente, LigneVente, DemandeReappro
)
from application_multi_magasins.serializers import (
    MagasinSerializer, ProduitSerializer, StockSerializer, VenteSerializer, LigneVenteSerializer, DemandeReapproSerializer
)

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class MagasinViewSet(viewsets.ModelViewSet):
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class VenteViewSet(viewsets.ModelViewSet):
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer

class LigneVenteViewSet(viewsets.ModelViewSet):
    queryset = LigneVente.objects.all()
    serializer_class = LigneVenteSerializer

class DemandeReapproViewSet(viewsets.ModelViewSet):
    queryset = DemandeReappro.objects.all()
    serializer_class = DemandeReapproSerializer

class RapportVentesAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'rapport_de_ventes.html'

    def get(self, request, format=None):
        # Récupération du magasin central à exclure
        centre = get_object_or_404(Magasin, nom='CENTRE_LOGISTIQUE')
        
        # Calcul des ventes par magasin (excluant le centre)
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
        
        # Calcul des produits les plus vendus (top 5)
        produits_populaires = (
            LigneVente.objects
            .values('produit__nom')
            .annotate(total_vendu=Sum('quantite'))
            .order_by('-total_vendu')[:5]
        )
        
        # Stock restant (excluant le centre)
        stock_restant = (
            Stock.objects.exclude(magasin=centre)
            .values('magasin__nom', 'produit__nom', 'quantite')
            .order_by('magasin__nom')
        )

        # Si le format demandé est JSON, renvoyer une réponse sérialisée
        if format == 'json' or request.accepted_renderer.format == 'json':
            return Response({
                'ventes_par_magasin': list(ventes_par_magasin),
                'produits_populaires': list(produits_populaires),
                'stock_restant': list(stock_restant)
            })
        # Sinon, renvoyer le contexte pour le template HTML
        return Response({
            'ventes_par_magasin': ventes_par_magasin,
            'produits_populaires': produits_populaires,
            'stock_restant': stock_restant
        })


class StockMagasinAPIView(APIView):
    # On autorise les deux renderers
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'stock_magasin.html'

    def get(self, request, magasin_id, format=None):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        # Pour optimiser l'accès aux données liées, utilisez select_related(si besoin)
        stocks = Stock.objects.filter(magasin=magasin).select_related('produit')
        
        # Si le paramètre `format` est spécifié et vaut 'json', on renvoie les données sérialisées.
        if format == 'json' or request.accepted_renderer.format == 'json':
            return Response({
                'magasin': MagasinSerializer(magasin).data,
                'stocks': StockSerializer(stocks, many=True).data
            })
        # Sinon, on renvoie le contexte pour le template HTML.
        return Response({'magasin': magasin, 'stocks': stocks})
    
class DashboardAPIView(APIView):
    """
    Vue RESTful pour le tableau de bord des performances.
    
    Cette vue fournit plusieurs agrégations:
      - chiffre_affaires: Total des ventes par magasin.
      - ruptures_stock: Stocks en rupture (quantité <= 5).
      - surstock: Produits en surstock (quantité >= 100).
      - tendances: Ventes des 7 derniers jours par magasin.
    
    La réponse est renvoyée en JSON par défaut. En cas de besoin, la vue peut également
    utiliser un template HTML (via TemplateHTMLRenderer).
    """
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'dashboard.html'  # Optionnel : un template HTML si on souhaite un rendu côté serveur.

    def get(self, request, format=None):
        # 1. Chiffre d'affaires par magasin
        chiffre_affaires = Vente.objects.values('magasin__nom').annotate(
            total=Sum(
                ExpressionWrapper(
                    F('lignes__quantite') * F('lignes__prix_unitaire'),
                    output_field=DecimalField()
                )
            )
        ).order_by('magasin__nom')
        
        # 2. Alertes de rupture de stock : on considère rupture si quantite ≤ 5
        ruptures_stock = Stock.objects.filter(quantite__lte=5).values(
            'magasin__nom', 'produit__nom', 'quantite'
        ).order_by('magasin__nom')
        
        # 3. Produits en surstock : on considère surstock si quantite ≥ 100
        surstock = Stock.objects.filter(quantite__gte=100).values(
            'magasin__nom', 'produit__nom', 'quantite'
        ).order_by('magasin__nom')
        
        # 4. Tendances hebdomadaires : ventes des 7 derniers jours par magasin
        now = timezone.now()
        one_week_ago = now - timedelta(days=7)
        tendances = Vente.objects.filter(created_at__gte=one_week_ago).values('magasin__nom').annotate(
            total_ventes=Sum(
                ExpressionWrapper(
                    F('lignes__quantite') * F('lignes__prix_unitaire'),
                    output_field=DecimalField()
                )
            )
        ).order_by('magasin__nom')
        
        result = {
            'chiffre_affaires': list(chiffre_affaires),
            'ruptures_stock': list(ruptures_stock),
            'surstock': list(surstock),
            'tendances': list(tendances)
        }
        
        # Si la requête demande du JSON (via ?format=json ou Accept: application/json), on renvoie du JSON.
        if format == 'json' or request.accepted_renderer.format == 'json':
            return Response(result)
        
        # Sinon, on peut aussi rendre un template HTML avec le contexte.
        return Response(result)

class ReapproAPIView(APIView):
    """
    Endpoint GET servant à récupérer les informations d'un stock
    pour la page de réapprovisionnement.
    
    Exemple d'URL : /api/reappro/<stock_id>/?format=json
    Renvoie un JSON comportant les données suivantes :
      - produit: { id, nom }
      - magasin: { id, nom }
      - stock_local: quantité du stock courant
      - stock_central: par exemple, stock central disponible provenant du modèle Produit
    """
    # Nous autorisons le JSON (et éventuellement un rendu HTML via un template si besoin)
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'demande_reappro.html'  # facultatif si vous souhaitez un rendu HTML

    def get(self, request, stock_id, format=None):
        stock = get_object_or_404(Stock, id=stock_id)
        
        data = {
            'produit': {
                'id': stock.produit.id,
                'nom': stock.produit.nom,
            },
            'magasin': {
                'id': stock.magasin.id,
                'nom': stock.magasin.nom,
            },
            'stock_local': stock.quantite,
            # Ainsi, ici, nous supposons que la propriété "stock_central" existe sur le modèle Produit.
            'stock_central': getattr(stock.produit, 'stock_central', 0)
        }
        return Response(data)
    
class DemandeReapproAPIView(APIView):
    """
    Endpoint POST pour enregistrer une demande de réapprovisionnement.
    
    URL exemple : /api/demande_reappro_utilisateur/<stock_id>/
    Corps attendu (JSON) :
      { "quantite": <nombre entier> }
    
    Renvoie un message de confirmation et éventuellement l'ID du magasin auquel rediriger.
    """
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def post(self, request, stock_id, format=None):
        stock = get_object_or_404(Stock, id=stock_id)
        quantite = request.data.get('quantite')

        if quantite is None:
            return Response({'error': 'Quantité non spécifiée'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantite = int(quantite)
            if quantite < 1:
                raise ValueError("La quantité doit être au moins 1.")
        except (ValueError, TypeError):
            return Response({'error': 'Quantité invalide'}, status=status.HTTP_400_BAD_REQUEST)

        # Ici, nous créons une demande de réapprovisionnement.
        # Vous pouvez remplacer ce block par la logique métier désirée.
        demande = DemandeReappro.objects.create(stock=stock, quantite=quantite)

        data = {
            'message': 'Demande de réapprovisionnement soumise avec succès.',
            'magasin_id': stock.magasin.id
        }
        return Response(data, status=status.HTTP_201_CREATED)
