"""Point d'entrée de l'application de gestion de caisse."""

from .database import populate_if_produit_empty, setup_database, SessionLocal
from .caisse import Caisse
from .interface import interface_caisse

def gestion_caisse(id_caisse):
    """
    Gère une session de caisse spécifique identifiée par son ID.
    Initialise une session de base de données et démarre l'interface.
    """
    session = SessionLocal()
    try:
        print(f"[Caisse {id_caisse}] Prête")
        pos = Caisse(session)
        interface_caisse(pos)
    finally:
        session.close()
        print(f"[Caisse {id_caisse}] Fermée")

def menu_principal():
    """
    Affiche le menu principal permettant de choisir une caisse à ouvrir.
    Initialise la base de données avant d'afficher le menu.
    """
    setup_database()
    populate_if_produit_empty()
    while True:
        print("\nMenu Principal :")
        print("1. Caisse 1")
        print("2. Caisse 2")
        print("3. Caisse 3")
        print("4. Quitter")
        choix = input("Choix : ")

        if choix == "1":
            gestion_caisse(1)
        elif choix == "2":
            gestion_caisse(2)
        elif choix == "3":
            gestion_caisse(3)
        elif choix == "4":
            print("Fermeture du système.")
            break
        else:
            print("Choix invalide")

if __name__ == "__main__":
    menu_principal()
