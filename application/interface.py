from caisse import Caisse

def interface_caisse(caisse):
    while True:
        print("\nMenu de la caisse :")
        print("1. Rechercher un produit")
        print("2. Enregistrer une vente")
        print("3. Traiter un retour")
        print("4. Consulter le stock")
        print("5. Quitter")
        choix = input("Choix : ")

        if choix == "1":
            identifiant = input("Identifiant (laisser vide si non applicable) : ") or None
            nom = input("Nom (laisser vide si non applicable) : ") or None
            categorie = input("Catégorie (laisser vide si non applicable) : ") or None
            caisse.rechercher_produit(identifiant, nom, categorie)
        elif choix == "2":
            produits = []
            while True:
                produit_id = input("ID du produit (ou 'q' pour terminer) : ")
                if produit_id.lower() == 'q':
                    break
                quantite = int(input("Quantité : "))
                produits.append((int(produit_id), quantite))
            caisse.enregistrer_vente(produits)
        elif choix == "3":
            vente_id = input("ID de la vente à annuler : ")
            caisse.gerer_retour(vente_id)
        elif choix == "4":
            caisse.consulter_stock()
        elif choix == "5":
            print("Fermeture de la caisse.")
            break
        else:
            print("Choix invalide")
