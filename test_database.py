import pytest
from sqlalchemy.exc import SQLAlchemyError
from application.database import setup_database, clear_and_populate_produit, SessionLocal
from application.tables import Produit, Base
from sqlalchemy import inspect

def test_setup_database():
    setup_database()
    inspector = inspect(SessionLocal().bind)
    assert 'produit' in inspector.get_table_names()

def test_clear_and_populate_produit():
    clear_and_populate_produit()

    session = SessionLocal()
    try:
        produits = session.query(Produit).all()
        assert len(produits) == 5
        noms = {p.nom for p in produits}
        assert "Product1" in noms
        assert "Product5" in noms
    finally:
        session.close()

def test_rollback_on_error(monkeypatch):
    # Simuler une erreur lors de session.commit()
    def raise_exception():
        raise SQLAlchemyError("Erreur simulée")

    monkeypatch.setattr("sqlalchemy.orm.Session.commit", lambda self: raise_exception())

    session = SessionLocal()
    try:
        initial_count = session.query(Produit).count()
    finally:
        session.close()

    # Appel de la fonction qui devrait échouer et rollback
    clear_and_populate_produit()

    # Vérifier que la base n’a pas été modifiée
    session = SessionLocal()
    try:
        new_count = session.query(Produit).count()
        assert new_count == initial_count  # Pas de changement dû à rollback
    finally:
        session.close()
