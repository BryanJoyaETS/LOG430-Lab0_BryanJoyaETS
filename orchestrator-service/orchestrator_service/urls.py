# orchestrator_service/urls.py
from django.urls import path
from orchestrator.views import OrderSagaAPIView

urlpatterns = [
    path("api/commande/", OrderSagaAPIView.as_view(), name="start-saga"),
]
