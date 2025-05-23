import psycopg2
import time
from decimal import Decimal

MAX_RETRIES = 10

# Connexion à PostgreSQL avec retry
for attempt in range(MAX_RETRIES):
    try:
        conn = psycopg2.connect(
            host="db",
            database="mydatabase",
            user="myuser",
            password="mypassword"
        )
        print("✅ Connexion réussie à la base de données PostgreSQL")
        break
    except Exception as e:
        print(f"Tentative {attempt + 1}/{MAX_RETRIES} : Erreur de connexion : {e}")
        time.sleep(3)
else:
    print("❌ Impossible de se connecter à la base après plusieurs tentatives.")
    exit(1)

cur = conn.cursor()

# Création de la table inventaire
cur.execute("""
    CREATE TABLE IF NOT EXISTS inventaire (
        id SERIAL PRIMARY KEY,
        nom TEXT NOT NULL,
        prix NUMERIC(10, 2) NOT NULL,
        quantite INT NOT NULL
    );
""")
conn.commit()

# Réinitialiser l'inventaire (pour les tests)
cur.execute("DELETE FROM inventaire;")
cur.execute("""
    INSERT INTO inventaire (nom, prix, quantite) VALUES
    ('Pomme', 0.50, 100),
    ('Banane', 0.30, 80),
    ('Pain', 2.00, 30),
    ('Lait', 1.50, 20);
""")
conn.commit()
print("✅ Inventaire initialisé")

# Simuler une vente : le client achète 2 pommes et 1 pain
panier = {
    "Pomme": 2,
    "Pain": 1
}

total = Decimal("0.0")

for produit, quantite_vendue in panier.items():
    cur.execute("SELECT prix, quantite FROM inventaire WHERE nom = %s;", (produit,))
    result = cur.fetchone()
    if result:
        prix_unitaire, quantite_dispo = result
        if quantite_dispo >= quantite_vendue:
            total += prix_unitaire * quantite_vendue
            cur.execute(
                "UPDATE inventaire SET quantite = quantite - %s WHERE nom = %s;",
                (quantite_vendue, produit)
            )
        else:
            print(f"❌ Stock insuffisant pour {produit}")
    else:
        print(f"❌ Produit introuvable : {produit}")

conn.commit()
print(f"💰 Total à payer : {total:.2f} €")

# Afficher l'inventaire mis à jour
print("\n📦 Inventaire mis à jour :")
cur.execute("SELECT nom, prix, quantite FROM inventaire ORDER BY id;")
for nom, prix, quantite in cur.fetchall():
    print(f"- {nom}: {prix:.2f} € | Stock: {quantite}")

# Fermer la connexion
cur.close()
conn.close()
