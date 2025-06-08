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
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages



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
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'stock_magasin.html'

    def get(self, request, magasin_id, format=None):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        stocks = Stock.objects.filter(magasin=magasin).select_related('produit')

        central_magasin = get_object_or_404(Magasin, nom="CENTRE_LOGISTIQUE")
        central_stocks = Stock.objects.filter(magasin=central_magasin).select_related('produit')

        if format == 'json' or request.accepted_renderer.format == 'json':
            return Response({
                'magasin': MagasinSerializer(magasin).data,
                'stocks': StockSerializer(stocks, many=True).data,
                'central_stocks': StockSerializer(central_stocks, many=True).data,
            })

        context = {
            'magasin': magasin,
            'stocks': stocks,
            'central_stocks': central_stocks,
        }
        return Response(context)
    
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
    template_name = 'tableau_de_bord.html'  # Optionnel : un template HTML si on souhaite un rendu côté serveur.

    def get(self, request, format=None):
        # 1. Chiffre d'affaires (excluant le magasin "CENTRE_LOGISTIQUE")
        chiffre_affaires = Vente.objects.exclude(magasin__nom="CENTRE_LOGISTIQUE") \
            .values('magasin__nom').annotate(
                total=Sum(
                    ExpressionWrapper(
                        F('lignes__quantite') * F('lignes__prix_unitaire'),
                        output_field=DecimalField()
                    )
                )
            ).order_by('magasin__nom')

        # 2. Alertes de rupture de stock (excluant le magasin "CENTRE_LOGISTIQUE")
        ruptures_stock = Stock.objects.exclude(magasin__nom="CENTRE_LOGISTIQUE") \
            .filter(quantite__lte=5) \
            .values('magasin__nom', 'produit__nom', 'quantite') \
            .order_by('magasin__nom')

        # 3. Produits en surstock (excluant le magasin "CENTRE_LOGISTIQUE")
        surstock = Stock.objects.exclude(magasin__nom="CENTRE_LOGISTIQUE") \
            .filter(quantite__gte=100) \
            .values('magasin__nom', 'produit__nom', 'quantite') \
            .order_by('magasin__nom')

        # Pour les tendances hebdomadaires sur les ventes des 7 derniers jours
        now = timezone.now()
        one_week_ago = now - timedelta(days=7)

        tendances = Vente.objects.exclude(magasin__nom="CENTRE_LOGISTIQUE") \
            .filter(date__gte=one_week_ago, date__lte=now) \
            .values('magasin__nom') \
            .annotate(total_quantite=Sum('lignes__quantite')) \
            .order_by('magasin__nom')

        result = {
            'chiffre_affaires': list(chiffre_affaires),
            'ruptures_stock': list(ruptures_stock),
            'surstock': list(surstock),
            'tendances': list(tendances)
        }

        if format == 'json' or request.accepted_renderer.format == 'json':
            return Response(result)

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

        # Récupération du magasin central
        try:
            central_magasin = Magasin.objects.get(nom="CENTRE_LOGISTIQUE")
        except Magasin.DoesNotExist:
            central_stock_qty = 0
        else:
            try:
                central_stock_obj = Stock.objects.get(magasin=central_magasin, produit=stock.produit)
                central_stock_qty = central_stock_obj.quantite
            except Stock.DoesNotExist:
                central_stock_qty = 0

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
            'stock_central': central_stock_qty,
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
    template_name = "demande_reappro_utilisateur.html"

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

        demande = DemandeReappro.objects.create(
            magasin=stock.magasin,
            produit=stock.produit,
            quantite=quantite,
            statut='pending'
        )

        data = {
            'message': 'Demande de réapprovisionnement soumise avec succès.',
            'magasin_id': stock.magasin.id
        }
        return Response(data, template_name=self.template_name, status=status.HTTP_201_CREATED)
    
class TraitementDemandeReapproAPIView(APIView):
    # On autorise le rendu HTML et JSON
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get_template_names(self):
        # Retourne la liste des templates possibles
        return ["traiter_demande_reappro.html"]

    def get(self, request, format=None):
        # Récupérer les demandes en attente (statut "pending")
        demandes = DemandeReappro.objects.filter(statut="pending") \
            .select_related("magasin", "produit")
        context = {"demandes": demandes}
        return Response(context)

    def post(self, request, format=None):
        # Récupérer l'ID de la demande et l'action envoyée depuis le formulaire
        demande_id = request.data.get("demande_id")
        action = request.data.get("action")
        demande = get_object_or_404(DemandeReappro, id=demande_id)

        # Traitement de l'action : approuver ou refuser
        if action == "approve":
            demande.statut = "approved"
            message_text = "Demande approuvée avec succès."
        elif action == "refuse":
            demande.statut = "refused"
            message_text = "Demande refusée avec succès."
        else:
            message_text = "Action invalide."
            messages.error(request, message_text)
            # On renvoie le contexte non modifié en cas d'erreur
            demandes = DemandeReappro.objects.filter(statut="pending") \
                .select_related("magasin", "produit")
            return Response({"demandes": demandes})

        # Enregistrer la modification et ajouter un message flash
        demande.save()
        messages.success(request, message_text)
        demandes = DemandeReappro.objects.filter(statut="pending") \
            .select_related("magasin", "produit")
        context = {"demandes": demandes}
        return Response(context)


class DemandeReapproActionAPIView(APIView):
    """
    POST  /api/demandes/<int:demande_id>/action/
    Corps JSON attendu: { "action": "approve" } ou { "action": "refuse" }
    
    - Si l'action est "approve", vérifie la quantité disponible dans le magasin CENTRE_LOGISTIQUE,
      transfère la quantité demandée dans le magasin concerné et supprime la demande.
    - Si l'action est "refuse", supprime simplement la demande.
    """
    def post(self, request, demande_id, format=None):
        # Récupération de la demande
        demande = get_object_or_404(DemandeReappro, id=demande_id)
        
        action = request.data.get("action")
        if action not in ['approve', 'refuse']:
            return Response({"error": "Action invalide."}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'approve':
            # Récupère le magasin central "CENTRE_LOGISTIQUE"
            central_magasin = get_object_or_404(Magasin, nom="CENTRE_LOGISTIQUE")
            
            try:
                central_stock = Stock.objects.get(magasin=central_magasin, produit=demande.produit)
            except Stock.DoesNotExist:
                return Response(
                    {"error": "Stock central indisponible pour ce produit."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifie que le stock central est suffisant
            if central_stock.quantite < demande.quantite:
                return Response(
                    {"error": "Stock central insuffisant pour cette demande."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mise à jour du stock central en soustrayant la quantité demandée
            central_stock.quantite -= demande.quantite
            central_stock.save()
            
            # Mise à jour (ou création) du stock dans le magasin du demandeur
            try:
                local_stock = Stock.objects.get(magasin=demande.magasin, produit=demande.produit)
            except Stock.DoesNotExist:
                local_stock = Stock.objects.create(
                    magasin=demande.magasin,
                    produit=demande.produit,
                    quantite=0
                )
            
            local_stock.quantite += demande.quantite
            local_stock.save()
            
            message_text = "Demande approuvée, stock transféré du centre logistique avec succès."
            
        else:  # action == 'refuse'
            message_text = "Demande refusée avec succès."
        
        demande.delete()
        
        return Response({"message": message_text}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Produit
from .serializers import ProduitSerializer

class ListeProduitsAPIView(APIView):
    """
    GET /api/produit/list/?format=json ou ?format=html
    Renvoie la liste des produits.
    
    - En mode HTML, le template 'liste_produits.html' est utilisé.
    - En mode JSON, la liste est sérialisée.
    """
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "liste_produits.html"  # Template pour le rendu HTML

    def get(self, request, format=None):
        produits = Produit.objects.all().order_by('nom')
        serializer = ProduitSerializer(produits, many=True)
        
        # Si le rendu HTML est demandé, renvoyer le contexte pour le template.
        if request.accepted_renderer.format == 'html':
            context = {'produits': produits}
            return Response(context, template_name=self.template_name)
        
        # Sinon, renvoyer la réponse JSON.
        return Response(serializer.data, status=status.HTTP_200_OK)

class ModifierProduitAPIView(APIView):
    """
    GET et PUT /api/produit/<int:produit_id>/modifier/?format=json ou ?format=html
    - GET : renvoie les détails d'un produit
    - PUT : met à jour le produit avec les données envoyées
      En mode HTML, le template 'modifier_produit.html' est utilisé pour afficher les données et les erreurs.
    """
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "modifier_produit.html"  # Template pour le rendu HTML

    def get(self, request, produit_id, format=None):
        produit = get_object_or_404(Produit, id=produit_id)
        serializer = ProduitSerializer(produit)
        
        if request.accepted_renderer.format == 'html':
            context = {'produit': produit}
            return Response(context, template_name=self.template_name)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, produit_id, format=None):
        produit = get_object_or_404(Produit, id=produit_id)
        serializer = ProduitSerializer(produit, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            message = "Produit mis à jour avec succès !"
            if request.accepted_renderer.format == 'html':
                context = {'produit': serializer.instance, 'message': message}
                return Response(context, template_name=self.template_name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if request.accepted_renderer.format == 'html':
                context = {'produit': produit, 'errors': serializer.errors}
                return Response(context, template_name=self.template_name)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
