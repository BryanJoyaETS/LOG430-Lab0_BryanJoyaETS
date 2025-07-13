# pylint: disable=no-member, import-error, too-few-public-methods
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from reports.models import (
    Magasin, Stock, Vente, LigneVente
)
@method_decorator(cache_page(60 * 5), name='dispatch')
class RapportVentesAPIView(APIView):
    """API pour le rapport des ventes."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'rapport_de_ventes.html'

    def get(self, request, response_format=None):
        """GET: Retourne le rapport des ventes."""
        logger.info("Génération du rapport des ventes")
        print("vue recalcuée")
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

