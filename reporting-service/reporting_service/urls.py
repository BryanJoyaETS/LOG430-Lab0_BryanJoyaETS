from django.contrib import admin
from django.urls import path, re_path
from reports.views import RapportVentesAPIView, DashboardAPIView
from django_prometheus import exports
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Reporting Service",
        default_version="v1",
        description="Documentation de l'API REST",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # UC1 – Générer un rapport consolidé des ventes
    path('ventes/', RapportVentesAPIView.as_view(), name='rapport_ventes'),

    # UC3 – Visualiser les performances des magasins
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),

    path("metrics/", exports.ExportToDjangoView),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),

]