# LOG430-Lab0_BryanJoyaETS

## Laboratoire 5 — Passage à une architecture microservices avec API Gateway et Observabilité

> **Note :** Le fichier de documentation principal se trouve dans  
> [`docs/Laboratoire5/README.md`](../Laboratoire5/README.md)

---

# Microservices – Laboratoire 5

## Résumé  
Dans ce laboratoire, j'ai déployé une architecture micro-services. Chaque service (Produits, Stocks, Carts, Accounts, Reporting) tourne en conteneur et dispose de son propre domaine de responsabilité :  
- **Produits** : Liste des fiches produit et modification 
- **Stocks** : Affichage des stocks des magasins,gestion demandes de réapprovisionnement
- **Carts** : enregistrement des ventes, retours , historique de transaction 
- **Accounts** : création et gestion des comptes clients via les fonctionnalités natives à Django
- **Reporting** : consolidation des rapports de ventes et tableau de bord
- **Application Multi Magasin** : Ex-monolithe, s'occupe de la page principale et de naviguer entre les différents services. Expose aussi toutes ses données.

Un **API Gateway** Nginx assure le routage vers chaque service, applique les règles CORS, et distribue la charge (round-robin). J'ai mis en place :

- **Service Discovery statique** via `upstream` Nginx  
- **Routage** `/api/produits/`, `/api/stock/`, `/api/caisse/`, `/api/clients/`, `/api/rapport/`  
- **En-têtes CORS** globaux (origines et méthodes autorisées)

L’observabilité s’appuie sur **Prometheus** (scraping de tous les `/metrics/` Django) et **Grafana** (dashboards p95, RPS, taux d’erreur), complétée par des tests de montée en charge **k6**.  
Enfin, j'ai  expérimenté un cache Redis sur la vue de stock.

## Objectifs  
1. **Découpage DDD**  
   - Bounded contexts identifiés  
   - Chaque service gère son propre schéma (ou son propre ensemble de tables)  
   - Malheureusement, il est difficile dans mon architecture courante de modifier les données entre plusieurs services. Je ne l'ai donc pas encore faire puisqu'il s'agit de la matière abordé dans le prochain laboratoire.

2. **API Gateway**  
   - Point d’entrée unique  
   - Routage statique vers les micro-services  
   - Politique CORS   

3. **Cache**  
   - Redis + `@cache_page` pour réduire la latence des appels des services  

4. **Tests de charge & observabilité**  
   - Montée en charge progressive avec k6 (30 s→20 VU, 60 s→50 VU, descente)  
   - Seuils p95 < 200 ms, taux d’échecs < 10 %  
   - Dashboards Grafana couvrant RPS, latence p95, taux d’erreur

5. **CI/CD & Infrastructure**  
   - Docker Compose pour tous les services  
   - GitHub Actions (lint, tests, builds Docker)  


## Exécution du projet

```bash
docker compose build --no-cache
RUN_TESTS=false docker compose  up -d
```
---
Une fois l'application démarrée, se rendre à l'adresse pour le site principal:  
[http://localhost:8000](http://localhost:8000)

Mon dashboard Graphana :
[http://localhost:3000/dashboards](http://localhost:3000/dashboards)

Mon scraping Prometheus :

Les targets : [http://10.194.32.198:9090/targets](http://10.194.32.198:9090/targets)

Résultats de mesure Graphana : 

[`docs/Laboratoire5/Graphana/analyse_resultats.md`](../Laboratoire5/Graphana/analyse_resultats.md)

ADRs : 

[`docs/Laboratoire5/ADR`](../Laboratoire5/ADR)


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
- **Laboratoire 5 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab5

---

## Documentation technique
