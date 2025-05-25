def interface_caisse(caisse):
    while True:
        print("\nMenu de la caisse :")
        print("1. Rechercher un produit")
        print("2. Enregistrer une vente")
        print("3. Traiter un retour")
        print("4. Consulter le stock")
        print("5. Consulter l'historique des transactions")
        print("6. Quitter")
        choix = input("Choix : ")

        if choix == "1":
            identifiant = input("Identifiant (laisser vide si non applicable) : ") or None
            nom = input("Nom (laisser vide si non applicable) : ") or None
            categorie = input("Catégorie (laisser vide si non applicable) : ") or None

            # Convertir identifiant en int si non vide
            try:
                identifiant = int(identifiant) if identifiant else None
            except ValueError:
                print("Identifiant invalide.")
                continue

            caisse.rechercher_produit(identifiant, nom, categorie)

        elif choix == "2":
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

        elif choix == "3":
            vente_id = input("ID de la vente à annuler : ")
            try:
                vente_id = int(vente_id)
                caisse.gerer_retour(vente_id)
            except ValueError:
                print("ID de vente invalide.")

        elif choix == "4":
            caisse.consulter_stock()

        elif choix == "5":
            caisse.consulter_historique_transactions()

        elif choix == "6":
            print("Fermeture de la caisse.")
            break
        else:
            print("Choix invalide")