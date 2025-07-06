from django.contrib import admin
from django.urls import path
from reports.views import RapportVentesAPIView, DashboardAPIView

urlpatterns = [
    path('admin/', admin.site.urls),

    # UC1 – Générer un rapport consolidé des ventes
    path('ventes/', RapportVentesAPIView.as_view(), name='rapport_ventes'),

    # UC3 – Visualiser les performances des magasins
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
]