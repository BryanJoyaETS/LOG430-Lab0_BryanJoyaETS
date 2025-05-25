from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import Base, Produit

DB_URL = "postgresql+psycopg2://myuser:mypassword@db:5432/mydatabase"

engine = create_engine(DB_URL, pool_size=10, max_overflow=5)
SessionLocal = sessionmaker(bind=engine)

def setup_database():
    Base.metadata.create_all(bind=engine)

def clear_and_populate_produit():
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
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()
