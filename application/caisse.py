import psycopg2
from database import create_connection

class Caisse:
    def __init__(self, conn):
        self.conn = conn

    def rechercher_produit(self, identifiant=None, nom=None, categorie=None):
        try:
            with self.conn.cursor() as cur:
                requete = "SELECT * FROM produit WHERE "
                conditions = []
                params = []

                if identifiant:
                    conditions.append("id = %s")
                    params.append(identifiant)
                if nom:
                    conditions.append("nom = %s")
                    params.append(nom)
                if categorie:
                    conditions.append("categorie = %s")
                    params.append(categorie)

                if not conditions:
                    requete = "SELECT * FROM produit"
                else:
                    requete += " AND ".join(conditions)

                cur.execute(requete, params)
                produits = cur.fetchall()
                for produit in produits:
                    print(produit)
        except psycopg2.Error as e:
            print(f"Erreur lors de la recherche du produit : {e}")

    def enregistrer_vente(self, produits):
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute("BEGIN")
                    cur.execute("INSERT INTO vente (date) VALUES (CURRENT_TIMESTAMP) RETURNING id")
                    id_vente = cur.fetchone()[0]

                    total = 0
                    for produit_id, quantite in produits:
                        cur.execute("SELECT stock, prix FROM produit WHERE id = %s FOR UPDATE", (produit_id,))
                        resultat = cur.fetchone()
                        if not resultat:
                            raise Exception("Produit non trouvé")
                        stock, prix = resultat
                        if stock < quantite:
                            raise Exception("Stock insuffisant")

                        cur.execute("""
                            INSERT INTO ligne_vente (vente_id, produit_id, quantite, prix_unitaire)
                            VALUES (%s, %s, %s, %s)
                        """, (id_vente, produit_id, quantite, prix))

                        cur.execute("""
                            UPDATE produit
                            SET stock = stock - %s
                            WHERE id = %s
                        """, (quantite, produit_id))

                        total += prix * quantite

                    print(f"Vente enregistrée (id_vente={id_vente}) — Total : {total} €")
        except Exception as e:
            self.conn.rollback()
            print(f"La vente a échoué : {e}")

    def gerer_retour(self, id_vente):
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute("SELECT produit_id, quantite FROM ligne_vente WHERE vente_id = %s", (id_vente,))
                    lignes_vente = cur.fetchall()

                    for produit_id, quantite in lignes_vente:
                        cur.execute("""
                            UPDATE produit
                            SET stock = stock + %s
                            WHERE id = %s
                        """, (quantite, produit_id))

                    cur.execute("DELETE FROM ligne_vente WHERE vente_id = %s", (id_vente,))
                    cur.execute("DELETE FROM vente WHERE id = %s", (id_vente,))

                    print("Retour traité avec succès")
        except psycopg2.Error as e:
            print(f"Erreur lors du traitement du retour : {e}")

    def consulter_stock(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM produit")
                produits = cur.fetchall()
                for produit in produits:
                    print(produit)
        except psycopg2.Error as e:
            print(f"Erreur lors de la consultation du stock : {e}")
