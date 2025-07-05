# pylint: disable=no-member, import-error, too-few-public-methods
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from produits.models import (
    Produit,
)
from produits.serializers import (
     ProduitSerializer,
)

class ListeProduitsAPIView(APIView):
    """API GET pour la liste des produits."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "liste_produits.html"

    def get(self, request, response_format=None):
        """GET: Retourne la liste des produits."""
        produits = Produit.objects.all().order_by('nom')
        serializer = ProduitSerializer(produits, many=True)
        if request.accepted_renderer.format == 'html':
            context = {'produits': produits}
            return Response(context, template_name=self.template_name)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ModifierProduitAPIView(APIView):
    """API GET/PUT pour modifier un produit."""
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "modifier_produit.html"

    def get(self, request, produit_id, response_format=None):
        """GET: Retourne les détails d'un produit."""
        produit = get_object_or_404(Produit, id=produit_id)
        serializer = ProduitSerializer(produit)
        if request.accepted_renderer.format == 'html':
            context = {'produit': produit}
            return Response(context, template_name=self.template_name)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, produit_id, response_format=None):
        """PUT: Met à jour un produit."""
        produit = get_object_or_404(Produit, id=produit_id)
        serializer = ProduitSerializer(produit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            message = "Produit mis à jour avec succès !"
            if request.accepted_renderer.format == 'html':
                context = {'produit': serializer.instance, 'message': message}
                return Response(context, template_name=self.template_name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.accepted_renderer.format == 'html':
            context = {'produit': produit, 'errors': serializer.errors}
            return Response(context, template_name=self.template_name, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
