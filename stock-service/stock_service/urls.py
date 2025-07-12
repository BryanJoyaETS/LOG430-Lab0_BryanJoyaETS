"""
URL configuration for stock_service project.

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
from django_prometheus import exports
from stocks.views import (
    StockMagasinAPIView, ReapproAPIView, TraitementDemandeReapproAPIView,
    DemandeReapproActionAPIView, DemandeReapproAPIView
)
urlpatterns = [
    path('admin/', admin.site.urls),

    # Stock d'un magasin  - UC2 consulter le stock d'un magasin spécifique
    path('api/stock/<int:magasin_id>/', StockMagasinAPIView.as_view(), name='stock_magasin'),

    # Page de demande de réapprovisionnement depuis un magasin
    path('api/stock/reappro/<int:stock_id>/', ReapproAPIView.as_view(), name='reappro'),
    
    # Traiter une demande de réapprovisionnement  - UC6 -Approvisionner un magasin depuis le centre logistique
    path('api/stock/demande/list/', TraitementDemandeReapproAPIView.as_view(), name='api_demandes_list'),
    path('api/stock/demandes/<int:demande_id>/action/', DemandeReapproActionAPIView.as_view(), name='api_demandes_action'),
    
    # Page de demande de réapprovisionnement pour un employé - UC5 - Demander un réapprovisionnement
    path('api/stock/demande_reappro_utilisateur/<int:stock_id>/', DemandeReapproAPIView.as_view(), name='demande_reappro_utilisateur'),
    path("metrics/", exports.ExportToDjangoView),

]
