from sqlalchemy.orm import Session
from datetime import datetime
from tables import Produit, Vente, LigneVente

class Caisse:
    def __init__(self, session: Session):
        self.session = session

    def rechercher_produit(self, identifiant: int | None = None, nom: str | None = None, categorie: str | None = None):
        try:
            query = self.session.query(Produit)
            if identifiant:
                query = query.filter(Produit.id == identifiant)
            if nom:
                query = query.filter(Produit.nom == nom)
            if categorie:
                query = query.filter(Produit.categorie == categorie)

            produits = query.all()
            for produit in produits:
                print(f"ID: {produit.id} | Nom: {produit.nom} | Catégorie: {produit.categorie} | Stock: {produit.stock} | Prix: {produit.prix}")
        except Exception as e:
            print(f"Erreur lors de la recherche du produit : {e}")

    def enregistrer_vente(self, produits: list[tuple[int, int]]):
        try:
            if self.session.in_transaction():
                self.session.commit()

            self.session.begin()
            vente = Vente(date=datetime.now())
            self.session.add(vente)
            self.session.flush()

            total = 0
            for produit_id, quantite in produits:
                produit = self.session.query(Produit).filter(Produit.id == produit_id).with_for_update().one_or_none()
                if not produit:
                    raise Exception(f"Produit {produit_id} non trouvé")
                if produit.stock < quantite:
                    raise Exception(f"Stock insuffisant pour le produit {produit.nom}")

                ligne = LigneVente(
                    vente_id=vente.id,
                    produit_id=produit.id,
                    quantite=quantite,
                    prix_unitaire=produit.prix
                )
                self.session.add(ligne)

                produit.stock -= quantite
                total += quantite * float(produit.prix)

            self.session.commit()
            print(f"Vente enregistrée (id_vente={vente.id}) — Total : {total:.2f} €")

        except Exception as e:
            self.session.rollback()
            print(f"La vente a échoué : {e}")
        
    def gerer_retour(self, id_vente: int):
        try:
            if self.session.in_transaction():
                self.session.commit()

            self.session.begin()
            lignes = self.session.query(LigneVente).filter_by(vente_id=id_vente).all()
            if not lignes:
                print("Aucune ligne de vente trouvée pour ce retour.")
                self.session.commit()
                return

            for ligne in lignes:
                produit = self.session.query(Produit).filter_by(id=ligne.produit_id).first()
                if produit:
                    produit.stock += ligne.quantite
                self.session.delete(ligne)

            vente = self.session.query(Vente).filter_by(id=id_vente).first()
            if vente:
                self.session.delete(vente)

            self.session.commit()
            print("Retour traité avec succès")

        except Exception as e:
            self.session.rollback()
            print(f"Erreur lors du traitement du retour : {e}")

    def consulter_stock(self):
        try:
            produits = self.session.query(Produit).order_by(Produit.id).all()
            for p in produits:
                print(f"ID: {p.id} | Nom: {p.nom} | Catégorie: {p.categorie} | Stock: {p.stock} | Prix: {p.prix}")
        except Exception as e:
            print(f"Erreur lors de la consultation du stock : {e}")

    def consulter_historique_transactions(self):
        try:
            ventes = self.session.query(Vente).order_by(Vente.date.desc()).all()

            if not ventes:
                print("Aucune transaction trouvée.")
                return

            for vente in ventes:
                print(f"ID Vente: {vente.id} | Date: {vente.date}")
                print("-" * 50)

                lignes = self.session.query(LigneVente).filter_by(vente_id=vente.id).all()

                total = 0
                for ligne in lignes:
                    produit = self.session.query(Produit).filter_by(id=ligne.produit_id).first()
                    if produit:
                        montant = ligne.quantite * ligne.prix_unitaire
                        total += montant
                        print(f"Produit: {produit.nom} | Quantité: {ligne.quantite} | Prix unitaire: {ligne.prix_unitaire} | Montant: {montant:.2f} €")

                print("-" * 50)
                print(f"Total de la vente: {total:.2f} €")
                print("\n")

        except Exception as e:
            print(f"Erreur lors de la consultation de l'historique des transactions : {e}")
         

