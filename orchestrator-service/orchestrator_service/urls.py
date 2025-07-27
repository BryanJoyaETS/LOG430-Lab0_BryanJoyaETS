# orchestrator_service/urls.py
from django.urls import path, include
from orchestrator.views import OrderSagaAPIView
from django_prometheus import exports


urlpatterns = [
    path("api/commande/", OrderSagaAPIView.as_view(), name="start-saga"),
    path("metrics/", exports.ExportToDjangoView),   

]
