# ADR 0002 : Choix de Redis pour le cache

## Statut  
Adopté

## Contexte  
Sur mon API Django, plusieurs endpoints critiques effectuent des requêtes coûteuses (agrégations dans rapport). Le temps de réponse et la charge CPU montaient fortement lors des pics de trafic.

## Décision  
Utiliser Redis comme cache centralisé pour stocker en mémoire les résultats de ces opérations lourdes.  

## Pourquoi Redis ?  
- Latence ultra-faible : données en RAM, accès en µs  
- TTL natif : expiration automatique des clés  
- Structures avancées : listes, sets, sorted sets pour cas d’usage futurs  

## Conséquences  
- Les endpoints mis en cache voient leur latence chuter drastiquement  
- Introduction d’un nouveau service à maintenir (configuration, monitoring, mémoire)  
- Nécessité de gérer l’invalidation des clés
- Renforcement global des performances et de la capacité à encaisser la charge  