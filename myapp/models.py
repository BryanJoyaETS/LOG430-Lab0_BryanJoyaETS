from django.db import models
from django.core.exceptions import ValidationError


class Magasin(models.Model):
    """
    Représente un magasin avec ses informations de base.

    Attributs :
      - nom : nom du magasin.
      - adresse : adresse du magasin.
    """
    nom = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    """
    Représente un produit en vente dans le magasin.

    Attributs :
      - nom : nom du produit.
      - categorie : catégorie à laquelle le produit appartient.
      - prix : prix unitaire du produit.
    """
    nom = models.CharField(max_length=255)
    categorie = models.CharField(max_length=255, blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nom


class Vente(models.Model):
    """
    Représente une vente effectuée.
    
    Attributs :
      - date : date et heure de la vente (définie au moment de la création).
      - magasin : magasin où la vente a eu lieu.
    """
    date = models.DateTimeField(auto_now_add=True)
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name='ventes')
    est_retournee = models.BooleanField(default=False)

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
    
class Stock(models.Model):
    """
    Représente le stock d'un produit dans un magasin.

    Attributs :
      - produit : produit en stock.
      - magasin : magasin où le produit est stocké.
      - quantite : quantité disponible du produit.
    """
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='stocks')
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name='stocks')
    quantite = models.IntegerField()

    def __str__(self):
        return f"{self.quantite} of {self.produit.nom} in {self.magasin.nom}"
    
    def clean(self):
        if self.quantite < 0:
            raise ValidationError("La quantité en stock ne peut pas être négative.")
        
class DemandeReappro(models.Model):
    STATUTS = (
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('refused', 'Refusée'),
    )
    magasin = models.ForeignKey('Magasin', on_delete=models.CASCADE, related_name='demandes_reappro')
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE, related_name='demandes_reappro')
    quantite = models.PositiveIntegerField()
    statut = models.CharField(max_length=10, choices=STATUTS, default='pending')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} pour {self.magasin.nom} ({self.get_statut_display()})"