# application_multi_magasins/api_views.py
from django.db import DatabaseError, transaction
from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import status

from .models import Magasin, Stock, Vente, LigneVente
from .serializers import (MagasinSerializer, StockSerializer,
                           VenteSerializer, LigneVenteSerializer)

# 2) Menu de la caisse pour un magasin donné (HTML + JSON)
class InterfaceCaisseAPIView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'menu_caisse.html'

    def get(self, request, magasin_id):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        # JSON: serializer
        if request.accepted_renderer.format == 'json':
            serializer = MagasinSerializer(magasin)
            return Response(serializer.data)
        # HTML: context
        return Response({'magasin': magasin})

# 3) Recherche produit (HTML form + JSON via POST)
class RechercheProduitAPIView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'recherche.html'

    def post(self, request, magasin_id):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        filtres = {}
        message_erreur = None
        resultats = None
        # Validation et filtres
        try:
            ident = request.data.get('identifiant')
            if ident:
                filtres['produit__id'] = int(ident)
        except ValueError:
            message_erreur = 'Identifiant invalide.'
        if 'nom' in request.data:
            filtres['produit__nom__icontains'] = request.data['nom']
        if 'categorie' in request.data:
            filtres['produit__categorie__icontains'] = request.data['categorie']
        if not filtres and not message_erreur:
            message_erreur = 'Veuillez remplir au moins un critère.'
        if not message_erreur:
            qs = Stock.objects.filter(magasin=magasin, **filtres).select_related('produit')
            if qs.exists():
                resultats = qs
            else:
                message_erreur = 'Aucun produit trouvé.'
        # JSON: renvoyer les stocks ou l'erreur
        if request.accepted_renderer.format == 'json':
            if message_erreur:
                return Response({'detail': message_erreur}, status=400)
            serializer = StockSerializer(resultats, many=True)
            return Response(serializer.data)
        # HTML: contexte
        return Response({
            'magasin': magasin,
            'resultats': resultats,
            'message_erreur': message_erreur
        })

# 4) Enregistrer une vente (HTML form + JSON via POST)
class EnregistrerVenteAPIView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'vente.html'

    def post(self, request, magasin_id):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        message = None
        data = request.data
        # Validation
        try:
            prod_id = int(data.get('produit_id'))
            quantite = int(data.get('quantite'))
            if quantite <= 0:
                raise ValueError()
        except (TypeError, ValueError):
            message = 'Les données saisies sont invalides.'
        if not message:
            try:
                stock = Stock.objects.get(magasin=magasin, produit__id=prod_id)
                if stock.quantite < quantite:
                    message = 'Stock insuffisant pour cette vente.'
                else:
                    with transaction.atomic():
                        vente = Vente.objects.create(magasin=magasin)
                        LigneVente.objects.create(
                            vente=vente,
                            produit=stock.produit,
                            quantite=quantite,
                            prix_unitaire=stock.produit.prix
                        )
                        stock.quantite -= quantite
                        stock.save()
                    message = f'Vente enregistrée : {quantite} x {stock.produit.nom}.'
            except Stock.DoesNotExist:
                message = 'Produit introuvable dans ce magasin.'
        # JSON
        if request.accepted_renderer.format == 'json':
            if message.startswith('Vente enregistrée'):
                serializer = VenteSerializer(vente)
                return Response(serializer.data, status=201)
            return Response({'detail': message}, status=400)
        # HTML
        return Response({'magasin': magasin, 'message': message})

# 5) Traiter un retour (HTML form + JSON via POST)
class TraiterRetourAPIView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'retour.html'

    def post(self, request, magasin_id):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        message = None
        try:
            vid = int(request.data.get('vente_id', ''))
            vente = Vente.objects.get(id=vid, magasin=magasin)
            with transaction.atomic():
                for ligne in vente.lignes.all():
                    stock, _ = Stock.objects.get_or_create(
                        magasin=magasin,
                        produit=ligne.produit,
                        defaults={'quantite': 0}
                    )
                    stock.quantite += ligne.quantite
                    stock.save()
                vente.delete()
            message = f'Vente {vid} annulée, stock mis à jour.'
        except (ValueError, Vente.DoesNotExist) as e:
            message = 'ID de vente invalide ou vente introuvable.'
        except DatabaseError:
            message = 'Erreur lors du traitement du retour.'
        # JSON
        if request.accepted_renderer.format == 'json':
            status_code = 200 if message.startswith('Vente') else 400
            return Response({'detail': message}, status=status_code)
        # HTML
        return Response({'magasin': magasin, 'message': message})

# 6) Historique des transactions (HTML + JSON)
class HistoriqueTransactionsAPIView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'historique.html'

    def get(self, request, magasin_id):
        magasin = get_object_or_404(Magasin, id=magasin_id)
        ventes = (Vente.objects.filter(magasin=magasin)
                  .order_by('-date')
                  .prefetch_related('lignes'))
        # JSON
        if request.accepted_renderer.format == 'json':
            serializer = VenteSerializer(ventes, many=True)
            return Response(serializer.data)
        # HTML
        return Response({'magasin': magasin, 'ventes': ventes})
