from django.contrib import admin
from django.urls import path, re_path
from accounts.views import register_view, UserCreateAPIView
from django_prometheus import exports

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Accounts Service",
        default_version="v1",
        description="Documentation de l'API REST",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/clients/register/', register_view, name='register'),

    path('api/clients/', UserCreateAPIView.as_view(), name='client_create'),
    path("metrics/", exports.ExportToDjangoView),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/clients/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/clients/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
  
]
