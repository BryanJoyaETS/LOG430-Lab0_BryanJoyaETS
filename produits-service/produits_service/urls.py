"""
URL configuration for produits_service project.

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
from produits.views import ListeProduitsAPIView, ModifierProduitAPIView
from django_prometheus import exports

urlpatterns = [
    path('admin/', admin.site.urls),
    # Lister les produits
    path('api/produits/list/', ListeProduitsAPIView.as_view(), name='liste_produits'),
    # Modifier un produit - UC4 - Modifier les informations d'un produit
    path('api/produits/<int:produit_id>/modifier/', ModifierProduitAPIView.as_view(), name='modifier_produit'),
    path("metrics/", exports.ExportToDjangoView),
]
