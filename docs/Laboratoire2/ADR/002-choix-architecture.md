# ADR 0002 : Choix d'une architecture monolithique

## Statut
Accepté

## Contexte
L’application doit gérer la logique métier, l’interface web et l’accès aux données pour un réseau de magasins, tout en restant simple à développer, déployer et maintenir.  
Le projet est réalisé dans un contexte avec des ressources limitées et un besoin de mise en oeuvre rapide.

## Décision
J'ai choisi une **architecture monolithique** :  
- Une seule application Django gère l’ensemble des fonctionnalités (modèles, vues, templates, logique métier).
- Pas de microservices, ni d’API REST séparée.

## Conséquences
- **Simplicité** du développement, du déploiement et de la maintenance.
- **Déploiement unifié** : une seule image Docker à gérer.
- **Moins de complexité** technique et opérationnelle.
- **Limites de scalabilité** : l’application ne peut pas être découpée horizontalement sans refonte.
- **Évolution** : toute nouvelle fonctionnalité s’ajoute dans le même codebase.

---