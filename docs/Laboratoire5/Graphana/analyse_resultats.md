k6 run k6/load-test.js

         /\      Grafana   /‾‾/  
    /\  /  \     |\  __   /  /   
   /  \/    \    | |/ /  /   ‾‾\ 
  /          \   |   (  |  (‾)  |
 / __________ \  |_|\_\  \_____/ 

     execution: local
        script: k6/load-test.js
        output: -

     scenarios: (100.00%) 1 scenario, 50 max VUs, 2m30s max duration (incl. graceful stop):
              * default: Up to 50 looping VUs for 2m0s over 3 stages (gracefulRampDown: 30s, gracefulStop: 30s)



  █ THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=18.24ms

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 6212    51.675963/s
    checks_succeeded...................: 100.00% 6212 out of 6212
    checks_failed......................: 0.00%   0 out of 6212

    ✓ stock 200
    ✓ rapport ventes 200

    HTTP
    http_req_duration.......................................................: avg=8.17ms min=2.03ms med=6.27ms max=182.68ms p(90)=14.31ms p(95)=18.24ms
      { expected_response:true }............................................: avg=8.17ms min=2.03ms med=6.27ms max=182.68ms p(90)=14.31ms p(95)=18.24ms
    http_req_failed.........................................................: 0.00%  0 out of 6212
    http_reqs...............................................................: 6212   51.675963/s

    EXECUTION
    iteration_duration......................................................: avg=1.01s  min=1s     med=1.01s  max=1.21s    p(90)=1.02s   p(95)=1.03s  
    iterations..............................................................: 3106   25.837981/s
    vus.....................................................................: 1      min=1         max=50
    vus_max.................................................................: 50     min=50        max=50

    NETWORK
    data_received...........................................................: 25 MB  203 kB/s
    data_sent...............................................................: 730 kB 6.1 kB/s




running (2m00.2s), 00/50 VUs, 3106 complete and 0 interrupted iterations
default ✓ [======================================] 00/50 VUs  2m0s


| Mesure                 | Avant (monolithe + LB)                                             | Après (micro‑services + LB)                                        |
|------------------------|---------------------------------------------------------------------|--------------------------------------------------------------------|
| **p95 latence**        | ~ 7 010 ms (seuil visé p95 < 500 ms non atteint)                   | ~ 18 ms (seuil p95 < 20 000 ms largement respecté)                 |
| **Latence moyenne**    | ~ 6 290 ms                                                          | ~ 8 ms                                                             |
| **RPS (débit)**        | ~ 2,98 req/s                                                        | ~ 51,6 req/s                                                       |
| **Taux d’erreur**      | 0 %                                                                 | 0 %                                                                |
| **VU max**             | 20                                                                  | 50                                                                 |
| **Itérations complètes** | 307 (environ 1 min)                                               | 6 212 (environ 2 min)                                             |

---

### 1. Avant (Monolithe + Load Balancer Nginx)
- **Configuration** : une unique instance Django servie derrière Nginx en round‑robin (1 réplique).  
- **Résultats k6** :  
  - 20 VUs simulés → 0 % d’erreur  
  - p95 ≃ 7 s, RPS ≃ 3 req/s  
- **Limites** :  
  - Goulot unique (une seule application)  
  - Absence de cache  
  - Charge CPU/mémoire saturée  

### 2. Après (Micro‑services + Load Balancer Nginx + Cache)
- **Configuration** :  
  - 5 services conteneurisés (Produits, Stocks, Carts, Accounts, Reporting)  
  - **Redis** pour le cache  
  - **Nginx** répartissant la charge sur les services  
- **Résultats k6** :  
  - Jusqu’à 50 VUs → 0 % d’erreur  
  - p95 ≃ 18 ms, latence moyenne ≃ 8 ms  
  - RPS ≃ 51 req/s  
