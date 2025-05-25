"""Fichier de test pour la classe Caisse"""

from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.tables import Base, Produit, Vente
from application.caisse import Caisse

# Crée une base en mémoire pour les tests
@pytest.fixture(scope="function")
def session():
    """Fixture de session SQLAlchemy avec base de données en mémoire"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

@pytest.fixture(scope="function")
def caisse(session):
    """Fixture pour la classe Caisse"""
    return Caisse(session)

def test_rechercher_produit(session, caisse):
    """Test de la recherche de produits"""
    p1 = Produit(nom="Lait", categorie="Alimentaire", stock=10, prix=1.5)
    p2 = Produit(nom="Savon", categorie="Hygiène", stock=5, prix=2.0)
    session.add_all([p1, p2])
    session.commit()

    caisse.rechercher_produit(nom="Lait")

def test_enregistrer_vente(session, caisse):
    """Test de l'enregistrement d'une vente"""
    p = Produit(nom="Pain", categorie="Alimentaire", stock=20, prix=1.0)
    session.add(p)
    session.commit()

    caisse.enregistrer_vente([(p.id, 3)])
    produit_mis_a_jour = session.query(Produit).get(p.id)
    assert produit_mis_a_jour.stock == 17

def test_gerer_retour(session, caisse):
    """Test de la gestion d'un retour"""
    produit = Produit(nom="Jus", categorie="Boissons", stock=10, prix=2.5)
    session.add(produit)
    session.commit()

    caisse.enregistrer_vente([(produit.id, 2)])
    vente = session.query(Vente).first()
    caisse.gerer_retour(vente.id)

    produit_apres_retour = session.query(Produit).get(produit.id)
    assert produit_apres_retour.stock == 10

def test_consulter_stock(session, caisse):
    """Test de la consultation du stock"""
    session.add(Produit(nom="Beurre", categorie="Alimentaire", stock=8, prix=2.0))
    session.commit()

    caisse.consulter_stock()

def test_consulter_historique_transactions(session, caisse):
    """Test de l'historique des ventes"""
    produit = Produit(nom="Café", categorie="Boissons", stock=10, prix=3.0)
    session.add(produit)
    session.commit()

    caisse.enregistrer_vente([(produit.id, 2)])
    caisse.consulter_historique_transactions()
