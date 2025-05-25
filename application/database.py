"""
Module database:
Gestion de la connexion à la base de données,
initialisation et peuplement des tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .tables import Base, Produit

DB_URL = "postgresql+psycopg2://myuser:mypassword@db:5432/mydatabase"

engine = create_engine(DB_URL, pool_size=10, max_overflow=5)
SessionLocal = sessionmaker(bind=engine)

def setup_database():
    """
    Crée toutes les tables dans la base de données définies par Base.metadata.
    """
    Base.metadata.create_all(bind=engine)

def clear_and_populate_produit():
    """
    Vide les tables existantes et insère des produits de démonstration.
    Gère les exceptions en rollback en cas d'erreur.
    """
    session = SessionLocal()
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        produits = [
            Produit(nom='Product1', categorie='Category1', stock=100, prix=10.99),
            Produit(nom='Product2', categorie='Category2', stock=200, prix=20.99),
            Produit(nom='Product3', categorie='Category3', stock=150, prix=15.99),
            Produit(nom='Product4', categorie='Category4', stock=300, prix=30.99),
            Produit(nom='Product5', categorie='Category5', stock=250, prix=25.99),
        ]
        session.add_all(produits)
        session.commit()
    except SQLAlchemyError as e:
        print(f"Erreur base de données : {e}")
        session.rollback()
    finally:
        session.close()
