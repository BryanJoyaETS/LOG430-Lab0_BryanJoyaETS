## Lancement du load-test.js : 

3.16 requêtes par secondes et 0.0667 req/s au repos

p99 : 24.7 secondes allant à 24.8,ms au repos
p95 : 23.5 secondes allant à 24.2 ms au repos

moyenne de 9.57s allant à 12.1s au maximum et 11.1ms au repos

charge CPU : 9.99%

Mémoire (RSS du process Django) en MiB
74.8

Total des réponses par endpoint
637
Réponses en Erreur
1.00
Taux d'erreur en %
0.158

execution: local
        script: k6/load-test.js
        output: -

     scenarios: (100.00%) 1 scenario, 50 max VUs, 2m30s max duration (incl. graceful stop):
              * default: Up to 50 looping VUs for 2m0s over 3 stages (gracefulRampDown: 30s, gracefulStop: 30s)



  █ THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=16.36s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 388     2.90593/s
    checks_succeeded...................: 100.00% 388 out of 388
    checks_failed......................: 0.00%   0 out of 388

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=10.07s min=606.29ms med=10.75s max=17.34s p(90)=15.89s p(95)=16.36s
      { expected_response:true }............................................: avg=10.07s min=606.29ms med=10.75s max=17.34s p(90)=15.89s p(95)=16.36s
    http_req_failed.........................................................: 0.00%  0 out of 388
    http_reqs...............................................................: 388    2.90593/s

    EXECUTION
    iteration_duration......................................................: avg=30.63s min=2.95s    med=32.89s max=47.14s p(90)=45.62s p(95)=46.32s
    iterations..............................................................: 123    0.92121/s
    vus.....................................................................: 4      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 1.0 MB 7.6 kB/s
    data_sent...............................................................: 78 kB  585 B/s




running (2m13.5s), 00/50 VUs, 123 complete and 8 interrupted iterations
default ✓ [======================================] 00/50 VUs  2m0s

![alt text](<captures/Capture d’écran 2025-06-28 162822.png>)



## Lancement du constant-load-test.js : 

![alt text](<captures/Capture d’écran 2025-06-28 173413.png>)

apres 
![alt text](<captures/Capture d’écran 2025-06-28 173856.png>)

execution: local
        script: k6/constant-load-test.js
        output: -

     scenarios: (100.00%) 1 scenario, 20 max VUs, 5m30s max duration (incl. graceful stop):
              * default: 20 looping VUs for 5m0s (gracefulStop: 30s)



  █ THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=7.01s

    http_req_failed
    ✓ 'rate<0.01' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 921     2.980015/s
    checks_succeeded...................: 100.00% 921 out of 921
    checks_failed......................: 0.00%   0 out of 921

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=6.29s  min=1.54s med=6.4s   max=7.96s  p(90)=6.85s  p(95)=7.01s 
      { expected_response:true }............................................: avg=6.29s  min=1.54s med=6.4s   max=7.96s  p(90)=6.85s  p(95)=7.01s 
    http_req_failed.........................................................: 0.00%  0 out of 921
    http_reqs...............................................................: 921    2.980015/s

    EXECUTION
    iteration_duration......................................................: avg=19.87s min=9.4s  med=20.11s max=21.42s p(90)=20.85s p(95)=20.98s
    iterations..............................................................: 307    0.993338/s
    vus.....................................................................: 2      min=2        max=20
    vus_max.................................................................: 20     min=20       max=20

    NETWORK
    data_received...........................................................: 2.4 MB 7.7 kB/s
    data_sent...............................................................: 183 kB 592 B/s




running (5m09.1s), 00/20 VUs, 307 complete and 0 interrupted iterations
default ✓ [======================================] 20 VUs  5m0s
ERRO[0309] thresholds on metrics 'http_req_duration' have been crossed 

## Lancement du soak-test.js : 

5 minutes dans l'endurance

![alt text](<captures/Capture d’écran 2025-06-28 174512.png>)

11 minutes : 
![alt text](<captures/Capture d’écran 2025-06-28 175133.png>)

23 minutes 

![alt text](<captures/Capture d’écran 2025-06-28 180326.png>)

 execution: local
        script: k6/soak-test.js
        output: -

     scenarios: (100.00%) 1 scenario, 10 max VUs, 30m30s max duration (incl. graceful stop):
              * default: 10 looping VUs for 30m0s (gracefulStop: 30s)



  █ THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<1000' p(95)=3.43s

    http_req_failed
    ✓ 'rate<0.02' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 5403    2.990182/s
    checks_succeeded...................: 100.00% 5403 out of 5403
    checks_failed......................: 0.00%   0 out of 5403

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=3s     min=656.57ms med=3.01s max=7.17s p(90)=3.32s  p(95)=3.43s
      { expected_response:true }............................................: avg=3s     min=656.57ms med=3.01s max=7.17s p(90)=3.32s  p(95)=3.43s
    http_req_failed.........................................................: 0.00%  0 out of 5403
    http_reqs...............................................................: 5403   2.990182/s

    EXECUTION
    iteration_duration......................................................: avg=10.02s min=6.98s    med=9.99s max=20.2s p(90)=10.53s p(95)=10.7s
    iterations..............................................................: 1801   0.996727/s
    vus.....................................................................: 5      min=5         max=10
    vus_max.................................................................: 10     min=10        max=10

    NETWORK
    data_received...........................................................: 14 MB  7.7 kB/s
    data_sent...............................................................: 1.1 MB 594 B/s




running (30m06.9s), 00/10 VUs, 1801 complete and 0 interrupted iterations
default ✓ [======================================] 10 VUs  30m0s
ERRO[1808] thresholds on metrics 'http_req_duration' have been crossed 

# Rapport d’analyse des tests de charge k6

## 1. Synthèse des résultats

| Test                    | VUs max | Durée  | RPS moyen  | p95 latence | Latence moyenne | CPU Django (%) | RSS (MiB) | Taux d’erreur |
|-------------------------|---------|--------|------------|-------------|-----------------|----------------|-----------|---------------|
| **Load-test (ramp-up)** | 50      | 2 min  | 2,9 req/s  | 16,4 s      | 10,1 s          | 9,99           | 74,8      | 0 %           |
| **Charge constante**    | 20      | 5 min  | 3,0 req/s  | 7,01 s      | 6,29 s          | ≃ 10           | 75        | 0 %           |
| **Endurance (soak)**    | 10      | 30 min | 3,0 req/s  | 3,43 s      | 3,00 s          | ≃ 10           | 75        | 0 %           |

> **Constats clés**  
> - Le débit plafonne autour de **3 req/s** quelles que soient le nombre de VUs.  
> - Les p95 restent élevées (3–16 s), alors que CPU/RAM ne sont pas saturés.  
> - Le taux d’erreur est négligeable

---

## 2. Points de friction (goulets d’étranglement)

1. **Requêtes lentes**  
   - Endpoint `/rapport/` effectue de lourdes agrégations sans index → séquences de `Seq Scan`.  

2. **Pool de connexions DB sous-dimensionné**  
   - Trop de VUs concurrents attendent une connexion libre → allongement de la latence globale.

3. **Absence de mise en cache**  
   - Chaque appel recalcule les mêmes résultats lourds (“cold path”) sans cache.

---


## Lancement du laod-test-2.js : 


5.5 minutes dans le test 

![alt text](<captures/Capture d’écran 2025-06-28 182707.png>)


vers la fin 

![alt text](<captures/Capture d’écran 2025-06-28 183113.png>)


THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=1m0s

    http_req_failed
    ✗ 'rate<0.01' rate=31.32%


  █ TOTAL RESULTS 

    HTTP
    http_req_duration.......................................................: avg=27.46s min=1.64s  med=23.6s max=1m0s   p(90)=1m0s   p(95)=1m0s  
      { expected_response:true }............................................: avg=16.08s min=1.64s  med=15.6s max=43.99s p(90)=30.22s p(95)=32.38s
    http_req_failed.........................................................: 31.32% 702 out of 2241
    http_reqs...............................................................: 2241   3.304146/s

    EXECUTION
    iteration_duration......................................................: avg=1m19s  min=10.26s med=1m21s max=3m1s   p(90)=2m22s  p(95)=2m40s 
    iterations..............................................................: 690    1.017341/s
    vus.....................................................................: 5      min=5           max=200
    vus_max.................................................................: 200    min=200         max=200

    NETWORK
    data_received...........................................................: 83 MB  123 kB/s
    data_sent...............................................................: 466 kB 687 B/s




running (11m18.2s), 000/200 VUs, 690 complete and 128 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s
ERRO[0681] thresholds on metrics 'http_req_duration, http_req_failed' have been crossed 


Sous un pic de 200 utilisateurs concurrents, l'application ne satisfait ni le critère de latence (p(95) < 500 ms) ni celui du taux d’échec (rate < 1 %) : en effet, 31 % des requêtes sont interrompues et la latence du 95ᵉ centile atteint systématiquement 60 s, valeur qui correspond au timeout par défaut de k6 et gonfle artificiellement nos percentiles. Ces timeouts massifs indiquent que, sous cette charge, le serveur ne peut pas traiter les requêtes dans les délais impartis et que beaucoup d’itérations restent inachevées, notamment en phase de rampe descendante où k6 n’accorde que 30 s pour terminer les appels en cours. Pour améliorer ces résultats, il conviendra d’abord d’ajuster le plan de test (allonger ou désactiver le timeout, augmenter le « gracefulRampDown » et distinguer phases de montée, palier et descente), puis de profiler l’API et l’infrastructure (CPU, mémoire, I/O, base de données, caches) afin d’identifier et de corriger les goulets d’étranglement avant de réhausser progressivement la charge.


## Analyse des points faibles et recommandations d’optimisation

- Pool de connexions saturé
    - Nombre de connexions ouvertes atteint rapidement le maximum configuré → file d’attente, latences accrues.
    - Pas de timeout ni de « recycle » sur les connexions inactives.
    - Absence ou insuffisance d’index
    - Requêtes de lecture sur les tables volumineuses (produits, stocks, rapports) déclenchent des parcours séquentiels (table scan).
    - Colonnes de filtre JOIN/FK non indexées (p. ex. produit_id, categorie_id) → lectures lentes.
- Requêtes SQL sous-optimales
    - Usage de SELECT * et récupération de champs non nécessaires pour l’API → surcharge réseau et CPU.
    - Jointures imbriquées sans condition de filtre préalable → explosion combinatoire de lignes en mémoire.
    - Absence de pagination sur les endpoints listant les rapports ou les historiques de stock.
- Absence de mise en cache
    - Appels répétés au même endpoint /rapport/ ou à la même ressource stock/produit sans cache → requêtes identiques refaites à chaque VU.
    - Aucun mécanisme de cache HTTP (ETag, Cache-Control) ni cache applicatif (Redis, in-memory).


## Recommandations d’amélioration
- Pool de connexions
    - Ajuster la taille du pool au besoin réel (souvent 2× le nombre de CPU) et définir un timeout court (30 s).
    - Activer un « connection lifetime » pour fermer les connexions longues et éviter la dérive.
- Indexation ciblée
    - Éviter les index superflus qui pénalisent les écritures ; privilégier les index couvrants sur un petit nombre de colonnes.
- Optimisation des requêtes SQL
    - Remplacer SELECT * par la liste explicite des champs nécessaires (SELECT id, nom, prix FROM produit WHERE id = ?).
    - Refactorer les requêtes lentes via EXPLAIN ANALYZE pour détecter les scans et large joins, puis :
    • Diviser les jointures complexes en CTE ou sous-requêtes filtrées.
    • Utiliser des fenêtres (window functions) pour les calculs agrégés, moins coûteux que des agrégations répétées.
    - Introduire la pagination (OFFSET+LIMIT ou keyset pagination) sur les listes longues pour limiter la taille des jeux de résultats.
- Mise en cache
    - Côté API, ajouter un cache en mémoire ou Redis pour les réponses fréquentes (TTL de quelques secondes à minutes selon la fraîcheur exigée).
    - Activer le cache HTTP (headers Cache-Control, ETag) pour permettre aux clients et aux proxy de conserver les résultats.
    - Mettre en place un cache de requêtes SQL (prepared statements avec plan de requête réutilisé) pour éviter la recompilation répétée.
