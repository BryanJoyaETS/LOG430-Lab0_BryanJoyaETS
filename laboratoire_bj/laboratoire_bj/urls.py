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
from myapp.views import index, recherche_produit, enregistrer_vente, traiter_retour, consulter_stock, historique_transactions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('recherche/', recherche_produit, name='recherche_produit'),
    path('vente/', enregistrer_vente, name='enregistrer_vente'),
    path('retour/', traiter_retour, name='traiter_retour'),
    path('stock/', consulter_stock, name='consulter_stock'),
    path('historique/', historique_transactions, name='historique_transactions'),

]
