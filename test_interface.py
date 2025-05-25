import pytest
from application.interface import interface_caisse
from application.caisse import Caisse
from application.tables import Base, Produit, Vente
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture(scope="function")
def caisse(session):
    return Caisse(session)

def test_menu_quit(monkeypatch, capsys, caisse):
    inputs = iter(["6"])  # choix "Quitter"
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    
    interface_caisse(caisse)
    captured = capsys.readouterr()
    assert "Fermeture de la caisse" in captured.out

def test_rechercher_produit(monkeypatch, capsys, caisse, session):
    # Ajouter un produit pour test
    p = Produit(nom="TestProd", categorie="TestCat", stock=10, prix=1.0)
    session.add(p)
    session.commit()

    inputs = iter([
        "1",        # choix : rechercher produit
        "",         # identifiant vide
        "TestProd", # nom
        "",         # catégorie vide
        "6"         # quitter
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    interface_caisse(caisse)
    captured = capsys.readouterr()
    assert "TestProd" in captured.out

def test_enregistrer_vente(monkeypatch, capsys, caisse, session):
    # Ajouter un produit pour test
    p = Produit(nom="ProdVente", categorie="CatVente", stock=5, prix=2.0)
    session.add(p)
    session.commit()

    inputs = iter([
        "2",        # choix : enregistrer une vente
        str(p.id),  # ID produit
        "3",        # quantité
        "q",        # fin saisie produits
        "6"         # quitter
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    interface_caisse(caisse)
    captured = capsys.readouterr()
    assert "Vente enregistrée" in captured.out
    # Vérifier le stock mis à jour
    prod = session.query(Produit).get(p.id)
    assert prod.stock == 2  # 5 - 3 = 2

from application.tables import Vente  # ajoute ça en haut si ce n'est pas déjà fait

def test_gerer_retour(monkeypatch, capsys, caisse, session):
    # Ajouter produit et enregistrer une vente
    p = Produit(nom="ProdRetour", categorie="CatRetour", stock=10, prix=1.5)
    session.add(p)
    session.commit()
    caisse.enregistrer_vente([(p.id, 2)])

    # Récupérer l'ID de la dernière vente
    vente = session.query(Vente).order_by(Vente.id.desc()).first()

    inputs = iter([
        "3",            # choix : gérer retour
        str(vente.id),  # id vente
        "6"             # quitter
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    interface_caisse(caisse)
    captured = capsys.readouterr()
    assert "Retour traité avec succès" in captured.out
    prod = session.get(Produit, p.id)
    assert prod.stock == 10  # stock rétabli après retour


def test_consulter_stock(monkeypatch, capsys, caisse, session):
    p = Produit(nom="ProdStock", categorie="CatStock", stock=7, prix=3.5)
    session.add(p)
    session.commit()

    inputs = iter([
        "4",  # consulter stock
        "6"   # quitter
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    interface_caisse(caisse)
    captured = capsys.readouterr()
    assert "ProdStock" in captured.out

def test_consulter_historique_transactions(monkeypatch, capsys, caisse, session):
    p = Produit(nom="ProdHist", categorie="CatHist", stock=10, prix=2.5)
    session.add(p)
    session.commit()
    caisse.enregistrer_vente([(p.id, 1)])

    inputs = iter([
        "5",  # consulter historique
        "6"   # quitter
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    interface_caisse(caisse)
    captured = capsys.readouterr()
    assert "ProdHist" in captured.out
    assert "Total de la vente" in captured.out
