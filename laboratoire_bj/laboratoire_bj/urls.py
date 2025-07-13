from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include, re_path
from application_multi_magasins.views import enregistrer_vente, historique_transactions, interface_caisse, recherche_produit, traiter_retour
from rest_framework.routers import DefaultRouter
from application_multi_magasins.api_views import (
    ProduitViewSet,
    MagasinViewSet,
    StockViewSet,
    VenteViewSet,
    LigneVenteViewSet,
    DemandeReapproViewSet,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.generic import TemplateView
from django_prometheus import exports

router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'magasins', MagasinViewSet, basename='magasin')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'ventes', VenteViewSet, basename='vente')
router.register(r'lignes', LigneVenteViewSet, basename='ligne')
router.register(r'demandes', DemandeReapproViewSet, basename='demande')

schema_view = get_schema_view(
    openapi.Info(
        title="API Gestion Magasins",
        default_version="v1",
        description="Documentation de l'API REST",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def liste_produits_view(request):
    return render(request, 'liste_produits.html')

def modifier_produit_view(request, produit_id):
    return render(request, 'modifier_produit.html', {'produit_id': produit_id})

urlpatterns = [
    path('api/monolithe/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/monolithe/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/monolithe/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("metrics/", exports.ExportToDjangoView),

]