from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include, re_path
from application_multi_magasins.views import enregistrer_vente, historique_transactions, interface_caisse, recherche_produit, traiter_retour
from rest_framework.routers import DefaultRouter
from application_multi_magasins.api_views import (
    DashboardAPIView,
    DemandeReapproAPIView,
    DemandeReapproActionAPIView,
    ListeProduitsAPIView,
    ModifierProduitAPIView,
    ProduitViewSet,
    MagasinViewSet,
    ReapproAPIView,
    StockViewSet,
    TraitementDemandeReapproAPIView,
    VenteViewSet,
    LigneVenteViewSet,
    DemandeReapproViewSet,
    RapportVentesAPIView,
    StockMagasinAPIView,
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

    path('api/', include(router.urls)),

    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    ## Cas d'usages exposés via l'API
    ##--------------------------------------------------------------------------------------------------------------------------
    # Rapport des ventes  - UC1 - Générer un rapport consolidé des ventes
    # path('api/rapport/', RapportVentesAPIView.as_view(), name='rapport_ventes'),
    # # Stock d'un magasin  - UC2 consulter le stock d'un magasin spécifique
    # path('api/stock/<int:magasin_id>/', StockMagasinAPIView.as_view(), name='stock_magasin'),
    # # Tableau de bord des magasins - UC3 - Visualiser les performances des magasins
    # path('api/dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    # # Page de demande de réapprovisionnement depuis un magasin
    # path('api/reappro/<int:stock_id>/', ReapproAPIView.as_view(), name='reappro'),
    
    # # Traiter une demande de réapprovisionnement  - UC6 -Approvisionner un magasin depuis le centre logistique
    # path('api/demande/list/', TraitementDemandeReapproAPIView.as_view(), name='api_demandes_list'),
    # path('api/demandes/<int:demande_id>/action/', DemandeReapproActionAPIView.as_view(), name='api_demandes_action'),
    
    # # Page de demande de réapprovisionnement pour un employé - UC5 - Demander un réapprovisionnement
    # path('api/demande_reappro_utilisateur/<int:stock_id>/', DemandeReapproAPIView.as_view(), name='demande_reappro_utilisateur'),

    # # Lister les produits
    # path('api/produit/list/', ListeProduitsAPIView.as_view(), name='liste_produits'),
    # # Modifier un produit - UC4 - Modifier les informations d'un produit
    # path('api/produit/<int:produit_id>/modifier/', ModifierProduitAPIView.as_view(), name='modifier_produit'),
    ##---------------------------------------------------------------------------------------------------------------------------
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # Documentation de l'API avec Swagger et ReDoc -----------------------------------------------------------------------------
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ##---------------------------------------------------------------------------------------------------------------------------
    # Fonctionnalités de l'interface caisse qui n'utilisent pas l'API
    # path('caisse/<int:magasin_id>/', interface_caisse, name='menu_caisse'),
    # # 1. Recherche de produit
    # path('caisse/<int:magasin_id>/recherche/',recherche_produit,name='recherche_produit'),
    # # 2. Enregistrer une vente
    # path('caisse/<int:magasin_id>/vente/',enregistrer_vente,name='enregistrer_vente'),
    # # 3. Traiter un retour
    # path('caisse/<int:magasin_id>/retour/',traiter_retour,name='traiter_retour'),
    # # 4. Historique des transactions
    # path('caisse/<int:magasin_id>/historique/',historique_transactions,name='historique_transactions'),


    ##-------------------------------------------metriques------------------------------------------------------------------------------
    path("metrics/", exports.ExportToDjangoView),

]