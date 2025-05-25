"""Définitions des modèles de base de données pour l'application de caisse."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Produit(Base):
    """
    Représente un produit en vente dans le magasin.

    Attributs :
        - id : identifiant unique du produit.
        - nom : nom du produit.
        - categorie : catégorie à laquelle le produit appartient.
        - stock : quantité en stock.
        - prix : prix unitaire du produit.
    """
    __tablename__ = 'produit'

    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    categorie = Column(String)
    stock = Column(Integer, nullable=False)
    prix = Column(Numeric(10, 2), nullable=False)

class Vente(Base):
    """
    Représente une vente effectuée.

    Attributs :
        - id : identifiant de la vente.
        - date : date et heure de la vente.
        - lignes : liste des produits vendus (relation avec LigneVente).
    """
    __tablename__ = 'vente'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    lignes = relationship("LigneVente", back_populates="vente")

class LigneVente(Base):
    """
    Représente une ligne dans une vente (un produit et sa quantité).

    Attributs :
        - id : identifiant de la ligne.
        - vente_id : identifiant de la vente associée.
        - produit_id : identifiant du produit vendu.
        - quantite : quantité vendue.
        - prix_unitaire : prix unitaire au moment de la vente.
    """
    __tablename__ = 'ligne_vente'

    id = Column(Integer, primary_key=True)
    vente_id = Column(Integer, ForeignKey('vente.id'))
    produit_id = Column(Integer, ForeignKey('produit.id'))
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Numeric(10, 2), nullable=False)

    vente = relationship("Vente", back_populates="lignes")
