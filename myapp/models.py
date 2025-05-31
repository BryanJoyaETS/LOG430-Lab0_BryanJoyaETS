from django.db import models

class Produit(models.Model):
    """
    Représente un produit en vente dans le magasin.

    Attributs :
      - nom : nom du produit.
      - categorie : catégorie à laquelle le produit appartient.
      - stock : quantité en stock.
      - prix : prix unitaire du produit.
    """
    nom = models.CharField(max_length=255)
    # categorie is optional; adjust max_length as needed.
    categorie = models.CharField(max_length=255, blank=True, null=True)
    stock = models.IntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nom


class Vente(models.Model):
    """
    Représente une vente effectuée.
    
    Attributs :
      - date : date et heure de la vente (définie au moment de la création).
    """
    # auto_now_add sets the field to now when the object is first created.
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vente {self.id} on {self.date}"


class LigneVente(models.Model):
    """
    Représente une ligne dans une vente (un produit et sa quantité).

    Attributs :
      - vente : vente associée.
      - produit : produit vendu.
      - quantite : quantité vendue.
      - prix_unitaire : prix unitaire au moment de la vente.
    """
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='lignes')
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} at {self.prix_unitaire}"