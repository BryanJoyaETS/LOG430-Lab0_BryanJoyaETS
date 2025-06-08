from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from application_multi_magasins.api_views import (
    DashboardAPIView,
    DemandeReapproAPIView,
    ProduitViewSet,
    MagasinViewSet,
    ReapproAPIView,
    StockViewSet,
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

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/rapport/', RapportVentesAPIView.as_view(), name='rapport_ventes'),
    path('api/stock/<int:magasin_id>/', StockMagasinAPIView.as_view(), name='stock_magasin'),
    path('api/dashboard/', DashboardAPIView.as_view(), name='dashboard'),

    
    path('api/reappro/<int:stock_id>/', ReapproAPIView.as_view(), name='reappro'),
    path('api/demande_reappro_utilisateur/<int:stock_id>/', DemandeReapproAPIView.as_view(), name='demande_reappro_utilisateur'),
   
    
    path('api/', include(router.urls)),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]