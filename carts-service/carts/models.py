# carts/models.py
from django.db import models

class Magasin(models.Model):
    nom     = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom       = models.CharField(max_length=255)
    categorie = models.CharField(max_length=255, blank=True, null=True)
    prix      = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom

class Stock(models.Model):
    magasin  = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name='stocks')
    produit  = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='stocks')
    quantite = models.IntegerField()

    def __str__(self):
        return f"{self.quantite} × {self.produit.nom} @ {self.magasin.nom}"

class Vente(models.Model):
    date          = models.DateTimeField(auto_now_add=True)
    magasin       = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name='ventes')
    est_retournee = models.BooleanField(default=False)

    def __str__(self):
        return f"Vente {self.id} – {self.magasin.nom} @ {self.date}"

class LigneVente(models.Model):
    vente         = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit       = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite      = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite}×{self.produit.nom} à {self.prix_unitaire}"

class DemandeReappro(models.Model):
    STATUTS = (
        ('pending',  'En attente'),
        ('approved', 'Approuvée'),
        ('refused',  'Refusée'),
    )
    magasin       = models.ForeignKey(Magasin, on_delete=models.CASCADE)
    produit       = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite      = models.PositiveIntegerField()
    statut        = models.CharField(max_length=10, choices=STATUTS, default='pending')
    date_demande  = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
