# Application de Gestion de Caisse

cloner le projet : git clone https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS.git

```text
Cette application simule un système de caisse pour un petit magasin, avec gestion des produits, des ventes, et des transactions en base de données. 
Elle est conçue pour fonctionner avec une base de données PostgreSQL et suit de bonnes pratiques de développement logiciel (CI/CD, tests automatisés, etc.).

il s'agit d'une application de type client/serveur a deux niveaux (2-tier), dans laquelle le client
est une application console locale qui interagit directement avec une base de donn´ees locale (le “serveur”).
```

# Instructions d'exécution 

1. Construire le conteneur : **docker compose build --no-cache** (on reconstruit au complet l'image pour s'assurer d'être à jour)

- toutes les installations requises devraient se télécharger lors du chargement du fichier requirements.txt dans le fichier Dockerfile
(pylint, pytest, sqlalchemy, psycopg2-binary==2.9.6)

2. Rouler le service client (nommé web) interactivement : **docker compose run web**

3. Vous devriez pouvoir intéragir avec la console et l'application de caisse !

-----------------------------------------Autres commandes---------------------------------------------------------------------------

4. Fermer les conteneurs actifs : **docker compose down**

5. Exécuter les tests : **docker compose build --no-cache**, puis **docker compose run web pytest**

6. Exécuter lint sur les fichiers principaux de l'application : **docker compose build --no-cache**, puis, **docker compose run web pylint application/**


# Choix technologiques
| Technologie                   | Rôle dans le projet               | Justification                                                                                     |
| ----------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Python 3.10+**              | Langage principal                 | Les dépendences nécessaires pour programmer en Pythonse trouvaient dans l'environnement de la VM  |
| **SQLAlchemy**                | ORM                               | Fournit une abstraction pour manipuler des bases SQL en objets Python.                            |
| **PostgreSQL**                | Base de données principale        | SGBD open source  pour les applications multi-utilisateurs.                                       |
| **SQLite**                    | Base légère pour les tests        | Ne nécessite pas d’installation, utilisée pour les tests unitaires locaux.                        |
| **Docker**                    | Conteneurisation de PostgreSQL    | Pour la conteneurisation du logiciel                                                              |
| **psycopg2**                  | Pilote PostgreSQL pour SQLAlchemy | Driver stable et utilisé pour la connexion à PostgreSQL via SQLAlchemy.                           |


