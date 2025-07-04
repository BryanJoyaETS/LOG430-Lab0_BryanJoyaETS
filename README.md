# LOG430-Lab0_BryanJoyaETS

## Laboratoire 5 —  Passage à une Architecture Microservices avec API Gateway etObservabilité

> **Note :** Le fichier de documentation principal se trouve dans  
> [`docs/Laboratoire4/README.md`](docs/Laboratoire5/README.md)

---

# Exposition d'API – Laboratoire 5

## Résumé

Ce laboratoire est une extension directe du Labo 3, avec pour objectif de faire évoluer
 votre système multi-magasins vers une architecture orientée microservices, adaptée à
 un contexte e-commerce.
 L’idée n’est pas d’ajouter une multitude de nouvelles fonctionnalités, mais de réorganiser
 les services existants, en y ajoutant quelques services propres au commerce en ligne.

# Objectifs pédagogiques

- Comprendre les fondements de l’architecture basée sur services (SBA) et microservices.
- Découper un système monolithique en services plus petits (sans réécrire toute la logique). Cloud Gateway...);
- la distinction entre les composantes du magasin physique (par exemple gestion des rayons, caisses, etc.) et celles d’un site e-commerce (compte client, panier, commande);
- Mettre en place une API Gateway (comme Kong, Spring Cloud Gateway, APISIX ou KrakenD).
- Configurer des routes vers les services internes.
- Protéger et documenter les points d’entrée via la Gateway


## Exécution du projet

```bash
docker compose -p lab3 build --no-cache
docker compose -p lab3 up -d db
docker compose -p lab3 up -d redis
RUN_TESTS=false docker compose -p lab3 up -d scale web=4
```
---
Une fois l'application démarrée, se rendre à l'adresse pour le site principal:  
[http://10.194.32.198:8000](http://10.194.32.198:8000)

---


## Clonage des laboratoires précédents

- **Laboratoire 0 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab0
- **Laboratoire 1 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab1
- **Laboratoire 2 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab2
- **Laboratoire 3 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab3
- **Laboratoire 4 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab4

---