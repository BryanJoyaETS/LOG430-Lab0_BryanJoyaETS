# ADR 0001 : Choix de Nginx comme load balancer

## Statut  
Adopté

## Contexte  
Je déploie une API Django Rest Framework qui servait à la fois du JSON et HTML, et je voyais mes workers Django en surcharge sur le buffering et la distribution du trafic.

## Décision  
J’ai placé Nginx comme load balancer pour :
- Distribuer les requêtes vers mes instances   
- Appliquer du caching HTTP

Voici pourquoi j’ai préféré Nginx à d’autres solutions :

- Richesse des modules  
  Cache HTTP intégré, rate-limiting, metrics, TLS offloading.

- Simplicité de configuration  
  Syntaxe concise, facile à maintenir.


## Conséquences  
- Mes workers Django sont libérés des tâches réseau et fichiers  
- Les temps de réponse statiques chutent drastiquement  
- Un peu plus de config Nginx à maintenir, mais un déploiement plus solide.
