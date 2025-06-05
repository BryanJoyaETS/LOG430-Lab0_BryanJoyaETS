# Decision record template by Michael Nygard

This is the template in [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions).
You can use [adr-tools](https://github.com/npryce/adr-tools) for managing the ADR files.

# ADR 001 - Choix de la plateforme (PostgreSQL via Docker)

## Statut  
Accepté

## Contexte  
L’application de caisse doit permettre la gestion centralisée de plusieurs caisses, tout en garantissant la **cohérence des données** (produits, ventes, stock). Le choix d’une architecture **client-serveur** avec une base de données PostgreSQL permet de séparer proprement les responsabilités :  
- Interface utilisateur (client léger ou CLI),
- Logique métier (serveur),
- Persistance (base de données).

Cette architecture doit également permettre une **scalabilité** future (ex. ajout d’une interface web ou mobile), tout en assurant la **fiabilité des transactions**.

## Décision  
J'ai choisi d’utiliser **PostgreSQL** comme base de données relationnelle principale, et de l’exécuter via un **conteneur Docker**. Cela garantit un environnement stable, portable, et conforme aux règles du laboratoire.

## Consequences  
- La configuration de la base devient standardisée et reproductible.
- L'utilisation de Docker simplifie l'installation et l'isolation du SGBD.
- Les développeurs doivent avoir Docker installé et en fonctionnement.
- Une base de test plus légère (SQLite) sera utilisée dans les tests unitaires pour ne pas dépendre de l’infrastructure.