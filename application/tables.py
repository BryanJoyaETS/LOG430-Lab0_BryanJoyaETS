from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Produit(Base):
    __tablename__ = 'produit'

    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    categorie = Column(String)
    stock = Column(Integer, nullable=False)
    prix = Column(Numeric(10, 2), nullable=False)

class Vente(Base):
    __tablename__ = 'vente'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    lignes = relationship("LigneVente", back_populates="vente")

class LigneVente(Base):
    __tablename__ = 'ligne_vente'

    id = Column(Integer, primary_key=True)
    vente_id = Column(Integer, ForeignKey('vente.id'))
    produit_id = Column(Integer, ForeignKey('produit.id'))
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Numeric(10, 2), nullable=False)

    vente = relationship("Vente", back_populates="lignes")
