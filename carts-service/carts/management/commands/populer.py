"""
Module pour peupler la base de données avec des données de démonstration.
"""
# pylint: disable=no-member

from django.core.management.base import BaseCommand
from produits.models import Produit, Magasin, Stock


class Command(BaseCommand):
    """
    Commande pour appopuler les tables Magasin, Produit et Stock avec des données 
    de démonstration.
    """
    help = (
        "Peupler la table des produits, magasins et stocks avec des données "
        "d'exemple."
    )

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        if not Magasin.objects.exists():
            magasins = [
                Magasin(nom='Store1', adresse='123 Main St'),
                Magasin(nom='Store2', adresse='456 Elm St'),
                Magasin(nom='Store3', adresse='789 Oak St'),
                Magasin(nom='Store4', adresse='321 Pine St'),
                Magasin(nom='Store5', adresse='654 Maple St'),
                Magasin(nom='CENTRE_LOGISTIQUE', adresse='100 Warehouse Ave'),
            ]
            Magasin.objects.bulk_create(magasins)
            self.stdout.write(
                self.style.SUCCESS("Stores have been successfully populated.")
            )
        else:
            self.stdout.write("The 'magasin' table is already populated.")

        if not Produit.objects.exists():
            produits = [
                Produit(nom='Product1', categorie='Category1', prix=10.99),
                Produit(nom='Product2', categorie='Category2', prix=15.49),
                Produit(nom='Product3', categorie='Category1', prix=7.99),
                Produit(nom='Product4', categorie='Category3', prix=20.00),
                Produit(nom='Product5', categorie='Category2', prix=12.50),
                Produit(nom='Product6', categorie='Category1', prix=8.75),
            ]
            Produit.objects.bulk_create(produits)
            self.stdout.write(
                self.style.SUCCESS("Products have been successfully populated.")
            )
        else:
            self.stdout.write("The 'produit' table is already populated.")

        if not Stock.objects.exists():
            stocks = [
                Stock(
                    magasin=Magasin.objects.get(nom='Store1'),
                    produit=Produit.objects.get(nom='Product1'),
                    quantite=100
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='Store1'),
                    produit=Produit.objects.get(nom='Product2'),
                    quantite=50
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='Store2'),
                    produit=Produit.objects.get(nom='Product3'),
                    quantite=200
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='Store2'),
                    produit=Produit.objects.get(nom='Product4'),
                    quantite=67
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='Store3'),
                    produit=Produit.objects.get(nom='Product4'),
                    quantite=150
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='Store4'),
                    produit=Produit.objects.get(nom='Product5'),
                    quantite=80
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='Store5'),
                    produit=Produit.objects.get(nom='Product6'),
                    quantite=120
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='CENTRE_LOGISTIQUE'),
                    produit=Produit.objects.get(nom='Product1'),
                    quantite=1000
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='CENTRE_LOGISTIQUE'),
                    produit=Produit.objects.get(nom='Product2'),
                    quantite=1000
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='CENTRE_LOGISTIQUE'),
                    produit=Produit.objects.get(nom='Product3'),
                    quantite=1000
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='CENTRE_LOGISTIQUE'),
                    produit=Produit.objects.get(nom='Product4'),
                    quantite=1000
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='CENTRE_LOGISTIQUE'),
                    produit=Produit.objects.get(nom='Product5'),
                    quantite=1000
                ),
                Stock(
                    magasin=Magasin.objects.get(nom='CENTRE_LOGISTIQUE'),
                    produit=Produit.objects.get(nom='Product6'),
                    quantite=1000
                ),
            ]
            Stock.objects.bulk_create(stocks)
            self.stdout.write(
                self.style.SUCCESS("Stocks have been successfully populated.")
            )
        else:
            self.stdout.write("The 'stock' table is already populated.")
