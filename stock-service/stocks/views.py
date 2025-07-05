# pylint: disable=no-member, import-error, too-few-public-methods
import logging

logger = logging.getLogger(__name__)


from django.contrib import messages
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from stocks.models import Magasin, Stock, DemandeReappro
from stocks.serializers import MagasinSerializer, StockSerializer

@method_decorator(cache_page(60 * 5), name='dispatch')
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
        else:  
            message_text = "Demande refusée avec succès."
        demande.delete()
        return Response({"message": message_text}, status=status.HTTP_200_OK)


