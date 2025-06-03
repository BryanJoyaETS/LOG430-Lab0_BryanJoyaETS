"""
URL configuration for laboratoire_bj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from myapp.views import demande_reappro, generer_rapport, interface_caisse, recherche_produit, enregistrer_vente, tableau_bord, traiter_retour, historique_transactions, afficher_magasins, stock_magasin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', afficher_magasins, name='index'),
    path('rapport/', generer_rapport, name='generer_rapport'),
    path('dashboard/', tableau_bord, name='tableau_bord'),
    path('demande-reappro/<int:stock_id>/', demande_reappro, name='demande_reappro'),
    path('caisse/<int:magasin_id>/', interface_caisse, name='menu_caisse'),

    # 1. Recherche de produit
    path(
      'caisse/<int:magasin_id>/recherche/',
      recherche_produit,
      name='recherche_produit'
    ),

    # 2. Enregistrer une vente
    path(
      'caisse/<int:magasin_id>/vente/',
      enregistrer_vente,
      name='enregistrer_vente'
    ),

    # 3. Traiter un retour
    path(
      'caisse/<int:magasin_id>/retour/',
      traiter_retour,
      name='traiter_retour'
    ),

    # 4. Consulter le stock (vous l’aviez déjà)
    path(
      'caisse/<int:magasin_id>/stock/',
      stock_magasin,
      name='stock_magasin'
    ),

    # 5. Historique des transactions
    path(
      'caisse/<int:magasin_id>/historique/',
      historique_transactions,
      name='historique_transactions'
    ),

    path(
      "reappro/<int:stock_id>/",
      demande_reappro, 
      name="demande_reappro"
    ),


]
