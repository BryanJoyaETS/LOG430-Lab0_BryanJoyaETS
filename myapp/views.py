# myapp/views.py
from django.shortcuts import render
from .models import Produit

def index(request):
    # Query all product records from the database
    produits = Produit.objects.all()
    # Pass them to the template context under the key 'produits'
    return render(request, 'index.html', {'produits': produits})