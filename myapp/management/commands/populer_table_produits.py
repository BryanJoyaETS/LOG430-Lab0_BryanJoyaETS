from django.core.management.base import BaseCommand
from myapp.models import Produit

class Command(BaseCommand):
    help = "Populate the Produit table with demonstration data"

    def handle(self, *args, **kwargs):
        if not Produit.objects.exists():
            produits = [
                Produit(nom='Product1', categorie='Category1', stock=100, prix=10.99),
                Produit(nom='Product2', categorie='Category2', stock=200, prix=20.99),
                Produit(nom='Product3', categorie='Category3', stock=150, prix=15.99),
                Produit(nom='Product4', categorie='Category4', stock=300, prix=30.99),
                Produit(nom='Product5', categorie='Category5', stock=250, prix=25.99),
            ]
            Produit.objects.bulk_create(produits)
            self.stdout.write(self.style.SUCCESS("Products have been successfully populated."))
        else:
            self.stdout.write("The 'produit' table is already populated.")