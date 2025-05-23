import threading
from database import setup_database, create_connection, connection_pool, clear_and_populate_produit
from caisse import Caisse
from interface import interface_caisse

def gestion_caisse(id_caisse):
    conn = create_connection()
    if not conn:
        print(f"[Caisse {id_caisse}] Échec de la connexion")
        return

    print(f"[Caisse {id_caisse}] Prête")
    pos = Caisse(conn)
    interface_caisse(pos)
    connection_pool.putconn(conn)
    print(f"[Caisse {id_caisse}] Fermée")

def menu_principal():
    setup_database()
    clear_and_populate_produit()

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
