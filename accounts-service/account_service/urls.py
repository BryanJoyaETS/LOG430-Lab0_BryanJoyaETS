from django.contrib import admin
from django.urls import path
from accounts.views import register_view, UserCreateAPIView
from django_prometheus import exports

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/clients/register/', register_view, name='register'),

    path('api/clients/', UserCreateAPIView.as_view(), name='client_create'),
    path("metrics/", exports.ExportToDjangoView),
]
