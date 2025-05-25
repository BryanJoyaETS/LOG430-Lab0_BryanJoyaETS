# Decision record template by Michael Nygard

This is the template in [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions).
You can use [adr-tools](https://github.com/npryce/adr-tools) for managing the ADR files.

# ADR 002 - Séparation des responsabilités (présentation, logique métier, persistance)

## Statut
Accepté

## Contexte
Une bonne séparation des responsabilités est cruciale pour assurer la maintenabilité du code, faciliter les tests unitaires et envisager des évolutions futures.

## Décision  
Le projet adopte une **architecture en couches** :
- La **couche présentation** est responsable de l’interaction avec l’utilisateur (console).
- La **couche logique métier** gère les opérations comme la création de ventes, la gestion du stock, etc. (Voir la classe Caisse.py pour les différents services)
- La **couche persistance** s’appuie sur SQLAlchemy pour interagir avec la base de données.

## Consequences  
- Facilite la **testabilité** de chaque couche indépendamment.
- Permet une **évolutivité** dans les prochains laboratoires.
- Implique une **structure de projet** plus complexe à mettre en place dès le départ.