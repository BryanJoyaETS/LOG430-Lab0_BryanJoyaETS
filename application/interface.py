"""Interface en ligne de commande pour interagir avec la classe Caisse."""

def interface_caisse(caisse):
    """
    Affiche un menu interactif pour gérer les opérations de caisse :
    recherche de produits, ventes, retours, stock et historique.
    """
    def saisir_recherche():
        identifiant = input("Identifiant (laisser vide si non applicable) : ") or None
        nom = input("Nom (laisser vide si non applicable) : ") or None
        categorie = input("Catégorie (laisser vide si non applicable) : ") or None

        try:
            identifiant = int(identifiant) if identifiant else None
        except ValueError:
            print("Identifiant invalide.")
            return

        caisse.rechercher_produit(identifiant, nom, categorie)

    def saisir_vente():
        produits = []
        while True:
            produit_id = input("ID du produit (ou 'q' pour terminer) : ")
            if produit_id.lower() == 'q':
                break
            try:
                produit_id = int(produit_id)
                quantite = int(input("Quantité : "))
                produits.append((produit_id, quantite))
            except ValueError:
                print("Entrée invalide, veuillez entrer un entier.")
        if produits:
            caisse.enregistrer_vente(produits)
        else:
            print("Aucun produit enregistré.")

    def saisir_retour():
        vente_id = input("ID de la vente à annuler : ")
        try:
            vente_id = int(vente_id)
            caisse.gerer_retour(vente_id)
        except ValueError:
            print("ID de vente invalide.")

    actions = {
        "1": saisir_recherche,
        "2": saisir_vente,
        "3": saisir_retour,
        "4": caisse.consulter_stock,
        "5": caisse.consulter_historique_transactions,
        "6": lambda: print("Fermeture de la caisse.")
    }

    while True:
        print("\nMenu de la caisse :")
        print("1. Rechercher un produit")
        print("2. Enregistrer une vente")
        print("3. Traiter un retour")
        print("4. Consulter le stock")
        print("5. Consulter l'historique des transactions")
        print("6. Quitter")
        choix = input("Choix : ")

        action = actions.get(choix)
        if action:
            if choix == "6":
                action()
                break
            action()
        else:
            print("Choix invalide.")
