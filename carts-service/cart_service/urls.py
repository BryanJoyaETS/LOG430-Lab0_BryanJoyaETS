from django.urls import path, include
from . import views as cart_views
from rest_framework.routers import DefaultRouter
from carts.views import (
    CartReapproAPIView, MagasinViewSet, StockViewSet, VenteViewSet,
    RechercheProduitAPIView, EnregistrerVenteAPIView,
    TraiterRetourAPIView, HistoriqueTransactionsAPIView
)

router = DefaultRouter()
router.register('magasins', MagasinViewSet, basename='magasin')
router.register('stock',    StockViewSet,   basename='stock')
router.register('ventes',   VenteViewSet,   basename='vente')

urlpatterns = [
    # --- Front HTML “caisse” ---
    path('caisse/<int:magasin_id>/',                cart_views.interface_caisse,       name='interface_caisse'),
    path('caisse/<int:magasin_id>/recherche/',      cart_views.recherche_html,         name='recherche_html'),
    path('caisse/<int:magasin_id>/vente/',          cart_views.vente_html,             name='vente_html'),
    path('caisse/<int:magasin_id>/retour/',         cart_views.retour_html,            name='retour_html'),
    path('caisse/<int:magasin_id>/historique/',     cart_views.historique_html,        name='historique_html'),
    path('caisse/reappro/<int:stock_id>/',          cart_views.demande_reappro_html,   name='demande_reappro_html'),

    # --- API REST ---
    path('api/', include(router.urls)),
    path('api/caisse/<int:magasin_id>/recherche/',
         RechercheProduitAPIView.as_view(),        name='recherche_produit'),
    path('api/caisse/<int:magasin_id>/vente/',
         EnregistrerVenteAPIView.as_view(),        name='enregistrer_vente'),
    path('api/caisse/<int:magasin_id>/retour/',
         TraiterRetourAPIView.as_view(),           name='traiter_retour'),
    path('api/caisse/<int:magasin_id>/historique/',
         HistoriqueTransactionsAPIView.as_view(),  name='historique_transactions'),
    path('api/reappro/<int:stock_id>/',
         CartReapproAPIView.as_view(),             name='api_reappro'),
]
