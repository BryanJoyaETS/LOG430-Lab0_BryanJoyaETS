"""
Tests unitaires pour les modèles SQLAlchemy définis dans app/tables.py.
Utilise une base SQLite en mémoire pour isoler les tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.tables import Base, Produit, Vente, LigneVente

@pytest.fixture(scope="module")
def session():
    """
    Crée une session de base SQLite en mémoire pour les tests.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    yield sess
    sess.close()

def test_create_produit(session):
    produit = Produit(nom="Chips", categorie="Snack", stock=50, prix=1.99)
    session.add(produit)
    session.commit()

    produit_db = session.query(Produit).filter_by(nom="Chips").first()
    assert produit_db is not None
    assert produit_db.stock == 50
    assert float(produit_db.prix) == 1.99

def test_create_vente_et_ligne_vente(session):
    produit = Produit(nom="Soda", categorie="Boisson", stock=100, prix=2.50)
    session.add(produit)
    session.commit()

    vente = Vente()
    ligne = LigneVente(
        produit_id=produit.id,
        quantite=3,
        prix_unitaire=produit.prix
    )
    vente.lignes.append(ligne)

    session.add(vente)
    session.commit()

    vente_db = session.query(Vente).first()
    assert vente_db is not None
    assert len(vente_db.lignes) == 1
    assert vente_db.lignes[0].quantite == 3
    assert float(vente_db.lignes[0].prix_unitaire) == 2.50
