from django.contrib import admin
from django.urls import path
from carts.views import (
    InterfaceCaisseAPIView,
    RechercheProduitAPIView,
    EnregistrerVenteAPIView,
    TraiterRetourAPIView,
    HistoriqueTransactionsAPIView,
)
from django_prometheus import exports

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
]