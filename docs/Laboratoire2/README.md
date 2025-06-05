### cloner le projet : git clone https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS.git


## Exécution du projet

```bash
docker compose build --no-cache
docker compose up -d db
RUN_TESTS=false docker compose up
```

-------------------------------------------------------------------------------------

## 1. Introduction et objectifs

### 1.1 Présentation
Application de gestion de magasins et caisses développée dans le cadre du laboratoire LOG430.

### 1.2 Objectifs d'architecture
- Fournir une solution simple, maintenable et évolutive.
- Gérer les stocks, les ventes, les réapprovisionnements.
- Produire des rapports consolidés pour un réseau de magasins.

## 2. Contraintes

- Technologies imposées : Python 3.11, Django, PostgreSQL, Docker.
- Déploiement via Docker Compose.
- Architecture simple pour répondre aux besoins essentiels.
- Accès restreint à certaines fonctionnalités pour des raisons de sécurité.

## 3. Contexte

### 3.1 Contexte métier
- Employés de caisse
- Responsables logistiques
- Administrateurs

### 3.2 Contexte technique
- Application Django (interface web, logique métier, gestion des flux)
- Base de données PostgreSQL (entités métier, transactions, stocks)

## 4. Solution architecturale

### 4.1 Vue d'ensemble
Architecture MVC typique de Django :
- **Models :** entités métier (Magasin, Produit, Stock, Vente, etc.)
- **Views :** logique métier et gestion des requêtes
- **Templates :** pages HTML générées

### 4.2 Composants
- Backend : Django (Python)
- Frontend : Django Templates (HTML/CSS)
- Base de données : PostgreSQL
- Orchestration : Docker Compose

### 5. Scénarios d'utilisation

### 5.1 Scénarios implémentés
- UC1 : Générer un rapport consolidé des ventes
- UC2 : Consulter le stock d'un magasin et déclencher un réapprovisionnement
- UC3 : Visualiser les performances des magasins dans un tableau
- UC4 : Mettre à jour les produits
- UC6 : Valider une commande de réapprovisionnement
- UC8 : Offrir une interface web minimale

### 5.2 Scénarios non-implémentés
- UC7 : Alerter automatiquement la maison mère en cas de rupture de stock critique

## 6. Décisions architecturales

- Framework Django : rapidité de développement, ORM intégré
- PostgreSQL : robuste et compatible Django
- Docker : isolation, portabilité, reproductibilité
- Architecture monolithique (pas de microservices ni API REST)

## 7. Vue de développement

Structure des dossiers :

- `myapp/` : application Django principale (models, views, templates, tests)
- `templates/` : HTML pour chaque fonctionnalité
- `docker-compose.yml` et `Dockerfile` : déploiement
- `tests.py` : tests unitaires des cas critiques

## 8. Vue de déploiement

Architecture conteneurisée :

- PostgreSQL et application web déployés via Docker Compose
- Lancement en deux étapes : d'abord la DB, puis le service 

Exécuter le projet : 

- docker compose build --no-cache
- docker compose up -d db
- RUN_TESTS=false docker compose up

Dans le cas d'un problème, simplement 

- CTRL+C et recommencer avec RUN_TESTS=false docker compose up

## 9. Vue opérations et maintenance

- Lancement rapide via Docker Compose
- Pipeline CI/CD avec linting, tests, build & push Docker
- Surveillance manuelle par logs et tests

## 10. Exigences qualité

- **Simplicité** : architecture directe, peu de dépendances
- **Évolutivité** : extensibilité Django
- **Testabilité** : tests automatisés (unitaires)
- **Déploiement rapide** : scripté et conteneurisé

## 11. Décisions d'architecture

- Architecture monolithique choisie pour la simplicité
- Refus de microservices et REST API pour limiter la complexité
- Gestion de configuration via fichiers standards Django

## 12. Risques et dettes techniques

- **Scalabilité** : non horizontale (monolithique)
- **Sécurité** : authentification/autorisation à implémenter
- **Expérience utilisateur** : à améliorer (messages d'erreur, validations)

## 13. Glossaire

- **MVC** : Modèle-Vue-Contrôleur
- **ORM** : Object-Relational Mapping
- **CI/CD** : Intégration continue / Déploiement continu
- **UC** : Cas d’utilisation