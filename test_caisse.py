import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.caisse import Caisse
from application.tables import Base, Produit, Vente


# Fixture pour la session SQLAlchemy avec base en mémoire
@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Fixture pour une instance de Caisse
@pytest.fixture(scope="function")
def caisse(session):
    return Caisse(session)

# --- TESTS ---

def test_rechercher_produit(session, caisse, capsys):
    # Préparation
    p1 = Produit(nom="Lait", categorie="Alimentaire", stock=10, prix=1.5)
    p2 = Produit(nom="Savon", categorie="Hygiène", stock=5, prix=2.0)
    session.add_all([p1, p2])
    session.commit()

    # Test par nom
    caisse.rechercher_produit(nom="Lait")
    captured = capsys.readouterr()
    assert "Lait" in captured.out

    # Test par catégorie
    caisse.rechercher_produit(categorie="Hygiène")
    captured = capsys.readouterr()
    assert "Savon" in captured.out

def test_enregistrer_vente(session, caisse, capsys):
    produit = Produit(nom="Pain", categorie="Alimentaire", stock=20, prix=1.0)
    session.add(produit)
    session.commit()

    caisse.enregistrer_vente([(produit.id, 3)])
    captured = capsys.readouterr()

    # Vérifie la sortie et la mise à jour du stock
    assert "Vente enregistrée" in captured.out
    produit_mis_a_jour = session.query(Produit).get(produit.id)
    assert produit_mis_a_jour.stock == 17

def test_gerer_retour(session, caisse, capsys):
    # Ajout d'un produit et enregistrement d'une vente
    produit = Produit(nom="Jus", categorie="Boissons", stock=10, prix=2.5)
    session.add(produit)
    session.commit()

    caisse.enregistrer_vente([(produit.id, 2)])
    vente = session.query(Vente).first()

    # Retour
    caisse.gerer_retour(vente.id)
    captured = capsys.readouterr()
    assert "Retour traité avec succès" in captured.out

    # Stock rétabli
    produit_apres = session.query(Produit).get(produit.id)
    assert produit_apres.stock == 10

def test_consulter_stock(session, caisse, capsys):
    session.add(Produit(nom="Beurre", categorie="Alimentaire", stock=8, prix=2.0))
    session.commit()

    caisse.consulter_stock()
    captured = capsys.readouterr()
    assert "Beurre" in captured.out

def test_consulter_historique_transactions(session, caisse, capsys):
    produit = Produit(nom="Café", categorie="Boissons", stock=10, prix=3.0)
    session.add(produit)
    session.commit()

    caisse.enregistrer_vente([(produit.id, 2)])
    caisse.consulter_historique_transactions()
    captured = capsys.readouterr()
    assert "Café" in captured.out
    assert "Total de la vente" in captured.out
