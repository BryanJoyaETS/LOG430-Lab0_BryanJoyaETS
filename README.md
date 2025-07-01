# LOG430-Lab0_BryanJoyaETS

## Laboratoire 4 — Load Balancing, Caching, Tests de charge et Observabilité

> **Note :** Le fichier de documentation principal se trouve dans  
> [`docs/Laboratoire4/README.md`](docs/Laboratoire4/README.md)

---

# Exposition d'API – Laboratoire 4

## Résumé

Ce laboratoire avait pour objectif d’améliorer les performances et la résilience d’une API RESTful multi-magasins en appliquant trois optimisations successives :
- Instrumentation et test de charge
- Répartition de charge et mise à l’échelle horizontale
- Mise en cache des endpoints critiques


## Objectifs
- Mettre en place une observabilité fine (Prometheus + Grafana)
- Identifier les goulets d’étranglement initiaux
- Assurer une montée en charge fluide via un load balancer
- Réduire la latence et la charge serveur grâce au caching


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

Mon dashboard Graphana :
[http://localhost:3000/dashboards](http://localhost:3000/dashboards)

Mon scraping Prometheus :
[http://10.194.32.198:8000/metrics/](http://10.194.32.198:8000/metrics/)

Les targets : [http://10.194.32.198:9090/targets](http://10.194.32.198:9090/targets)

Scripts de test de charge : 

[`k6/load-test.js`](k6/load-test.js)
[`k6/load-test-2.js`](k6/load-test-2.js)

Résultats de mesure et tableaux comparatifs : 

[`docs/Laboratoire4/resultats`](docs/Laboratoire4/resultats)

Synthèse et interpretation des résultats :

[`docs/Laboratoire4/synthèse_des_resultats`](docs/Laboratoire4/synthèse_des_resultats)

ADRs : 

[`docs/Laboratoire4/ADR`](docs/Laboratoire4/ADR)



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