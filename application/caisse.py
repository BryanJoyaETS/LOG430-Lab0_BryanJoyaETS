"""Module de gestion des opérations de caisse pour un magasin.

Ce module fournit la classe Caisse permettant :
- la recherche de produits,
- l'enregistrement des ventes,
- la gestion des retours,
- la consultation du stock,
- l'affichage de l'historique des transactions.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .tables import Produit, Vente, LigneVente


class Caisse:
    """Classe représentant une caisse de magasin."""

    def __init__(self, session: Session):
        """
        Initialise une instance de Caisse.

        :param session: Session SQLAlchemy active pour les opérations sur la base de données.
        """
        self.session = session

    def rechercher_produit(
        self,
        identifiant: int|None = None,
        nom: str|None = None,
        categorie: str|None = None
        ):
        """
        Recherche un ou plusieurs produits selon l'identifiant, le nom ou la catégorie.

        :param identifiant: ID du produit (optionnel)
        :param nom: Nom du produit (optionnel)
        :param categorie: Catégorie du produit (optionnel)
        """
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
                print(
                    f"ID: {produit.id} | "
                    f"Nom: {produit.nom} | "
                    f"Catégorie: {produit.categorie} | "
                    f"Stock: {produit.stock} | "
                    f"Prix: {produit.prix}"
                )
        except SQLAlchemyError as e:
            print(f"Erreur lors de la recherche du produit : {e}")

    def enregistrer_vente(self, produits: list[tuple[int, int]]):
        """
        Enregistre une vente et met à jour le stock des produits.

        :param produits: Liste de tuples (id_produit, quantité)
        """
        try:
            if self.session.in_transaction():
                self.session.commit()

            self.session.begin()
            vente = Vente(date=datetime.now())
            self.session.add(vente)
            self.session.flush()

            total = 0
            for produit_id, quantite in produits:
                produit = (
                    self.session.query(Produit)
                    .filter(Produit.id == produit_id)
                    .with_for_update()
                    .one_or_none()
                )
                if not produit:
                    raise ValueError(f"Produit {produit_id} non trouvé")
                if produit.stock < quantite:
                    raise ValueError(f"Stock insuffisant pour le produit {produit.nom}")

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

        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"La vente a échoué : {e}")

    def gerer_retour(self, id_vente: int):
        """
        Gère le retour d'une vente : réapprovisionne les stocks et supprime la vente.

        :param id_vente: Identifiant de la vente à annuler.
        """
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

        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Erreur lors du traitement du retour : {e}")

    def consulter_stock(self):
        """
        Affiche la liste de tous les produits avec leurs informations de stock.
        """
        try:
            produits = self.session.query(Produit).order_by(Produit.id).all()
            for p in produits:
                print(
                    f"ID: {p.id} | Nom: {p.nom} | Catégorie: {p.categorie} | "
                    f"Stock: {p.stock} | Prix: {p.prix}"
                )
        except SQLAlchemyError as e:
            print(f"Erreur lors de la consultation du stock : {e}")

    def consulter_historique_transactions(self):
        """
        Affiche l'historique de toutes les ventes enregistrées.
        """
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
                        print(
                            f"Produit: {produit.nom} | Quantité: {ligne.quantite} | "
                            f"Prix unitaire: {ligne.prix_unitaire}\n"
                            f"Montant: {montant:.2f} €"
                        )
                print("-" * 50)
                print(f"Total de la vente: {total:.2f} €")
                print("\n")

        except SQLAlchemyError as e:
            print(f"Erreur lors de la consultation de l'historique des transactions : {e}")
