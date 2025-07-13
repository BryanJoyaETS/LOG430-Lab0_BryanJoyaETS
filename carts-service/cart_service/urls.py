from django.contrib import admin
from django.urls import path, re_path
from carts.views import (
    InterfaceCaisseAPIView,
    RechercheProduitAPIView,
    EnregistrerVenteAPIView,
    TraiterRetourAPIView,
    HistoriqueTransactionsAPIView,
)
from django_prometheus import exports
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Carts Service",
        default_version="v1",
        description="Documentation de l'API REST",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    
    path('admin/', admin.site.urls),

    path(
        'api/caisse/<int:magasin_id>/',
        InterfaceCaisseAPIView.as_view(),
        name='interface_caisse_api'
    ),

    path(
        'api/caisse/<int:magasin_id>/recherche/',
        RechercheProduitAPIView.as_view(),
        name='recherche_produit'
    ),

    path(
        'api/caisse/<int:magasin_id>/vente/',
        EnregistrerVenteAPIView.as_view(),
        name='enregistrer_vente'
    ),

    path(
        'api/caisse/<int:magasin_id>/retour/',
        TraiterRetourAPIView.as_view(),
        name='traiter_retour'
    ),

    path(
        'api/caisse/<int:magasin_id>/historique/',
        HistoriqueTransactionsAPIView.as_view(),
        name='historique_transactions'
    ),
    path("metrics/", exports.ExportToDjangoView),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/caisse/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/caisse/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]