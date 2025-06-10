"""
Vues API RESTful

Ce module fournit des vues API RESTful pour la gestion des ressources Vue.
Il définit des points de terminaison pour créer, récupérer, mettre à jour et supprimer des objets Vue,
en suivant les conventions RESTful.
"""
# pylint: disable=no-member, import-error, too-few-public-methods
from datetime import timedelta

from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from application_multi_magasins.models import (
    Magasin, Produit, Stock, Vente, LigneVente, DemandeReappro
)
from application_multi_magasins.serializers import (
    MagasinSerializer, ProduitSerializer, StockSerializer, VenteSerializer,
    LigneVenteSerializer, DemandeReapproSerializer
)


class ProduitViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Produit."""
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer


class MagasinViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Magasin."""
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer


class StockViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Stock."""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class VenteViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle Vente."""
    queryset = Vente.objects.all()
    serializer_class = VenteSerializer


class LigneVenteViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle LigneVente."""
    queryset = LigneVente.objects.all()
    serializer_class = LigneVenteSerializer


class DemandeReapproViewSet(viewsets.ModelViewSet):
    """ViewSet pour le modèle DemandeReappro."""
    queryset = DemandeReappro.objects.all()
    serializer_class = DemandeReapproSerializer


class RapportVentesAPIView(APIView):
    """API pour le rapport des ventes."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'rapport_de_ventes.html'

    def get(self, request, response_format=None):
        """GET: Retourne le rapport des ventes."""
        centre = get_object_or_404(Magasin, nom='CENTRE_LOGISTIQUE')
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
        produits_populaires = (
            LigneVente.objects
            .values('produit__nom')
            .annotate(total_vendu=Sum('quantite'))
            .order_by('-total_vendu')[:5]
        )
        stock_restant = (
            Stock.objects.exclude(magasin=centre)
            .values('magasin__nom', 'produit__nom', 'quantite')
            .order_by('magasin__nom')
        )
        if response_format == 'json' or request.accepted_renderer.format == 'json':
            return Response({
                'ventes_par_magasin': list(ventes_par_magasin),
                'produits_populaires': list(produits_populaires),
                'stock_restant': list(stock_restant)
            })
        return Response({
            'ventes_par_magasin': ventes_par_magasin,
            'produits_populaires': produits_populaires,
            'stock_restant': stock_restant
        })


class StockMagasinAPIView(APIView):
    """API pour afficher le stock d'un magasin."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'stock_magasin.html'

    def get(self, request, magasin_id, response_format=None):
        """GET: Retourne le stock d'un magasin."""
        magasin = get_object_or_404(Magasin, id=magasin_id)
        stocks = Stock.objects.filter(magasin=magasin).select_related('produit')
        central_magasin = get_object_or_404(Magasin, nom="CENTRE_LOGISTIQUE")
        central_stocks = Stock.objects.filter(magasin=central_magasin).select_related('produit')
        if response_format == 'json' or request.accepted_renderer.format == 'json':
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
    """Vue RESTful pour le tableau de bord des performances."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'tableau_de_bord.html'

    def get(self, request, response_format=None):
        """GET: Retourne les agrégations pour le tableau de bord."""
        chiffre_affaires = Vente.objects.exclude(magasin__nom="CENTRE_LOGISTIQUE") \
            .values('magasin__nom').annotate(
                total=Sum(
                    ExpressionWrapper(
                        F('lignes__quantite') * F('lignes__prix_unitaire'),
                        output_field=DecimalField()
                    )
                )
            ).order_by('magasin__nom')
        ruptures_stock = Stock.objects.exclude(magasin__nom="CENTRE_LOGISTIQUE") \
            .filter(quantite__lte=5) \
            .values('magasin__nom', 'produit__nom', 'quantite') \
            .order_by('magasin__nom')
        surstock = Stock.objects.exclude(magasin__nom="CENTRE_LOGISTIQUE") \
            .filter(quantite__gte=100) \
            .values('magasin__nom', 'produit__nom', 'quantite') \
            .order_by('magasin__nom')
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
        if response_format == 'json' or request.accepted_renderer.format == 'json':
            return Response(result)
        return Response(result)


class ReapproAPIView(APIView):
    """API GET pour la page de réapprovisionnement."""
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'demande_reappro.html'

    def get(self, request, stock_id, response_format=None):
        """GET: Retourne les infos de stock pour réapprovisionnement."""
        stock = get_object_or_404(Stock, id=stock_id)
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
    """API POST pour enregistrer une demande de réapprovisionnement."""
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "demande_reappro_utilisateur.html"

    def post(self, request, stock_id, response_format=None):
        """POST: Crée une demande de réapprovisionnement."""
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
    """API pour traiter les demandes de réapprovisionnement."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get_template_names(self):
        """Retourne la liste des templates possibles."""
        return ["traiter_demande_reappro.html"]

    def get(self, request, response_format=None):
        """GET: Liste les demandes en attente."""
        demandes = DemandeReappro.objects.filter(statut="pending") \
            .select_related("magasin", "produit")
        context = {"demandes": demandes}
        return Response(context)

    def post(self, request, response_format=None):
        """POST: Traite une demande (approve/refuse)."""
        demande_id = request.data.get("demande_id")
        action = request.data.get("action")
        demande = get_object_or_404(DemandeReappro, id=demande_id)
        if action == "approve":
            demande.statut = "approved"
            message_text = "Demande approuvée avec succès."
        elif action == "refuse":
            demande.statut = "refused"
            message_text = "Demande refusée avec succès."
        else:
            message_text = "Action invalide."
            messages.error(request, message_text)
            demandes = DemandeReappro.objects.filter(statut="pending") \
                .select_related("magasin", "produit")
            return Response({"demandes": demandes})
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
    """
    def post(self, request, demande_id, response_format=None):
        """POST: Approuve ou refuse une demande de réapprovisionnement."""
        demande = get_object_or_404(DemandeReappro, id=demande_id)
        action = request.data.get("action")
        if action not in ['approve', 'refuse']:
            return Response({"error": "Action invalide."}, status=status.HTTP_400_BAD_REQUEST)
        if action == 'approve':
            central_magasin = get_object_or_404(Magasin, nom="CENTRE_LOGISTIQUE")
            try:
                central_stock = Stock.objects.get(magasin=central_magasin, produit=demande.produit)
            except Stock.DoesNotExist:
                return Response(
                    {"error": "Stock central indisponible pour ce produit."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if central_stock.quantite < demande.quantite:
                return Response(
                    {"error": "Stock central insuffisant pour cette demande."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            central_stock.quantite -= demande.quantite
            central_stock.save()
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


class ListeProduitsAPIView(APIView):
    """API GET pour la liste des produits."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "liste_produits.html"

    def get(self, request, response_format=None):
        """GET: Retourne la liste des produits."""
        produits = Produit.objects.all().order_by('nom')
        serializer = ProduitSerializer(produits, many=True)
        if request.accepted_renderer.format == 'html':
            context = {'produits': produits}
            return Response(context, template_name=self.template_name)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ModifierProduitAPIView(APIView):
    """API GET/PUT pour modifier un produit."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "modifier_produit.html"

    def get(self, request, produit_id, response_format=None):
        """GET: Retourne les détails d'un produit."""
        produit = get_object_or_404(Produit, id=produit_id)
        serializer = ProduitSerializer(produit)
        if request.accepted_renderer.format == 'html':
            context = {'produit': produit}
            return Response(context, template_name=self.template_name)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, produit_id, response_format=None):
        """PUT: Met à jour un produit."""
        produit = get_object_or_404(Produit, id=produit_id)
        serializer = ProduitSerializer(produit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            message = "Produit mis à jour avec succès !"
            if request.accepted_renderer.format == 'html':
                context = {'produit': serializer.instance, 'message': message}
                return Response(context, template_name=self.template_name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.accepted_renderer.format == 'html':
            context = {'produit': produit, 'errors': serializer.errors}
            return Response(context, template_name=self.template_name, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
