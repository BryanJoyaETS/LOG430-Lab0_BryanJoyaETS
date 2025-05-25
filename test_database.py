import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from application.database import setup_database, clear_and_populate_produit, SessionLocal
from application.tables import Produit, Vente, LigneVente

def test_setup_database():
    setup_database()
    inspector = inspect(SessionLocal().bind)
    tables = inspector.get_table_names()

    assert "produit" in tables
    assert "vente" in tables
    assert "ligne_vente" in tables

def test_clear_and_populate_produit():
    clear_and_populate_produit()
    session = SessionLocal()
    try:
        produits = session.query(Produit).all()
        assert len(produits) == 5
        noms = [p.nom for p in produits]
        assert "Product1" in noms
        assert "Product5" in noms
    finally:
        session.close()

def test_rollback_on_error(monkeypatch):
    # Simuler une erreur lors de session.commit()
    def raise_error(self):
        raise SQLAlchemyError("Erreur simulée")

    monkeypatch.setattr("sqlalchemy.orm.Session.commit", raise_error)

    session = SessionLocal()
    try:
        initial_count = session.query(Produit).count()
    finally:
        session.close()

    clear_and_populate_produit()  # Ne devrait rien ajouter à cause du rollback

    session = SessionLocal()
    try:
        final_count = session.query(Produit).count()
        assert final_count == initial_count
    finally:
        session.close()
