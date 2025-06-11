# Exposition d'API – Laboratoire 3

Ce projet expose plusieurs API RESTful pour la gestion d'un réseau de magasins, permettant la consultation, la modification et le suivi des stocks, produits, ventes et demandes de réapprovisionnement. Les API sont conçues pour être utilisées à la fois par des interfaces web (HTML) et des clients externes (JSON).

## Exécution du projet

```bash
docker compose -p lab3 build --no-cache
docker compose -p lab3 up -d db
RUN_TESTS=false docker compose -p lab3 up
```

Une fois l'application démarrée, se rendre à l'adresse :  
[http://10.194.32.198:8000](http://10.194.32.198:8000)

---

## Endpoints principaux

### 1. Tableau de bord des performances
- **URL :** `/api/dashboard/`
- **Méthodes :** `GET`
- **Formats :** JSON, HTML (`tableau_de_bord.html`)
- **Fonctionnalités :**
  - Chiffre d'affaires par magasin
  - Produits en rupture de stock
  - Produits en surstock
  - Tendances des ventes

### 2. Rapport consolidé des ventes
- **URL :** `/api/rapport/`
- **Méthodes :** `GET`
- **Formats :** JSON, HTML (`rapport_de_ventes.html`)
- **Fonctionnalités :**
  - Ventes par magasin
  - Produits les plus vendus
  - Stock restant par magasin

### 3. Gestion des produits
- **Lister les produits :** `/api/produit/list/` (`GET`)
- **Modifier un produit :** `/api/produit/<id>/modifier/` (`GET`, `PUT`)
- **Formats :** JSON, HTML (`modifier_produit.html`)

### 4. Gestion des stocks
- **Lister les stocks :** `/api/stocks/` (`GET`)
- **Consulter le stock d'un magasin :** `/api/stock/<magasin_id>/` (`GET`)

### 5. Réapprovisionnement
- **Demander un réapprovisionnement :** `/api/demande_reappro_utilisateur/<stock_id>/` (`POST`)
- **Traiter les demandes (approbation/refus) :** `/api/demande/list/` (`GET`, `POST`)
- **Action sur une demande :** `/api/demandes/<demande_id>/action/` (`POST`)

## Formats de réponse

- **JSON** : Pour intégration avec des clients externes ou du JavaScript.
- **HTML** : Pour affichage direct dans le navigateur via des templates Django.

## Sécurité

- Protection CSRF sur les endpoints (modification, création).
- Validation des données côté serveur (quantité, existence des objets, etc.).

## Tests

Des tests automatisés valident les comportements des API :
- Vérification des statuts HTTP
- Présence et format des données attendues
- Gestion des erreurs et des cas limites

## Documentation

- Documentation interactive disponible via Swagger à `http://10.194.32.198:8000/swagger/`.

---