## avec deux instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=2


## LOAD-TEST.JS : 

![alt text](<Capture d’écran 2025-06-29 204232.png>)


execution: local
        script: k6/load-test.js
        output: -

     scenarios: (100.00%) 1 scenario, 50 max VUs, 2m30s max duration (incl. graceful stop):
              * default: Up to 50 looping VUs for 2m0s over 3 stages (gracefulRampDown: 30s, gracefulStop: 30s)



  █ THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=16.3s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 378     2.874171/s
    checks_succeeded...................: 100.00% 378 out of 378
    checks_failed......................: 0.00%   0 out of 378

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=10.11s min=599.28ms med=10.69s max=16.84s p(90)=16.05s p(95)=16.3s 
      { expected_response:true }............................................: avg=10.11s min=599.28ms med=10.69s max=16.84s p(90)=16.05s p(95)=16.3s 
    http_req_failed.........................................................: 0.00%  0 out of 378
    http_reqs...............................................................: 378    2.874171/s

    EXECUTION
    iteration_duration......................................................: avg=30.81s min=2.87s    med=33.84s max=48.64s p(90)=45.78s p(95)=46.69s
    iterations..............................................................: 122    0.927642/s
    vus.....................................................................: 3      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 994 kB 7.6 kB/s
    data_sent...............................................................: 75 kB  568 B/s




running (2m11.5s), 00/50 VUs, 122 complete and 6 interrupted iterations
default ✓ [======================================] 00/50 VUs  2m0s


Le test de charge montre que le système est globalement stable sous une montée en charge progressive jusqu’à 50 utilisateurs virtuels. Aucune erreur HTTP n’a été enregistrée, ce qui indique une bonne robustesse du backend et du load balancer en mode round-robin. Toutefois, les temps de réponse restent élevés, avec une moyenne de 10,1 secondes et un 95ᵉ percentile atteignant 16,3 secondes. Cela suggère que, bien que le système tienne la charge sans planter, certaines opérations côté serveur (base de données, logique métier ou I/O) ralentissent les réponses. Une optimisation des performances backend serait donc souhaitable si l’objectif est d’améliorer l’expérience utilisateur ou de supporter plus de trafic à latence plus faible.

| **Métrique**       | **Après Load Balancer (2 instances)** |
| ------------------ | ------------------------------------- |
| **Trafic total**   | 0.740 req/s                           |
| **Erreurs (nb)**   | 222                                   |
| **Latence P99**    | 20 ms                                 |
| **CPU**            | 43.4%, 43.5%                          |
| **Mémoire Django** | 63.8 MB, 64.2 MB                      |


## Lancement du load-test-2.js : 

![alt text](<Capture d’écran 2025-06-29 212126.png>)
![alt text](<Capture d’écran 2025-06-29 212259.png>)

 THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=55.65s

    http_req_failed
    ✗ 'rate<0.01' rate=54.68%


  █ TOTAL RESULTS 

    checks_total.......................: 3893   5.733811/s
    checks_succeeded...................: 45.31% 1764 out of 3893
    checks_failed......................: 54.68% 2129 out of 3893

    ✗ stock 200
      ↳  46% — ✓ 626 / ✗ 717
    ✗ rapport 200
      ↳  46% — ✓ 599 / ✗ 693
    ✗ update 200
      ↳  42% — ✓ 539 / ✗ 719

    HTTP
    http_req_duration.......................................................: avg=15.72s min=291.14µs med=5.07s  max=1m0s   p(90)=42.9s p(95)=55.65s
      { expected_response:true }............................................: avg=24.33s min=649.23ms med=25.9s  max=59.58s p(90)=42.9s p(95)=48.18s
    http_req_failed.........................................................: 54.68% 2129 out of 3893
    http_reqs...............................................................: 3893   5.733811/s

    EXECUTION
    iteration_duration......................................................: avg=45.8s  min=1s       med=17.67s max=3m1s   p(90)=1m59s p(95)=2m15s 
    iterations..............................................................: 1255   1.848429/s
    vus.....................................................................: 2      min=2            max=200
    vus_max.................................................................: 200    min=200          max=200

    NETWORK
    data_received...........................................................: 67 MB  98 kB/s
    data_sent...............................................................: 776 kB 1.1 kB/s




running (11m19.0s), 000/200 VUs, 1255 complete and 118 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s

| Point clé                     | Ce qu'on vois                                                            | Ce que ça signifie                                                                                          |
| ----------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Seuils**                    | `p(95)<500 ms` et `rate<1 %`                                              | 95 % des requêtes prennent **≈ 56 s** ( > 500 ms) et plus d’une requête sur deux échoue : le test est raté. |
| **Taux d’erreur**             | `http_req_failed = 54,7 %`                                                | Environ 2100 réponses ne sont **pas** des 2xx/3xx.                                                          |
| **Répartition des checks**    | \~45 % seulement de « stock », « rapport », « update » retournent **200** | Plus de la moitié de chaque type d’appel finit en 4xx/5xx ou timeout.                                       |
| **Latence P95**               | ≈ 55 s                                                                    | La plupart des appels atteignent le **timeout de 60 s**.                                                    |
| **Durée moyenne d’itération** | \~46 s                                                                    | Chaque VU met près d’une minute pour boucler → gros goulot d’étranglement.                                  |
| **Charge injectée**           | Jusqu’à **200 VUs**                                                       | Les deux instances ne tiennent pas cette concurrence.                                                       |



## avec trois instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=3


## LOAD-TEST.JS : 

![alt text](<Capture d’écran 2025-06-29 220350.png>)

█ THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=16.58s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 381     2.838553/s
    checks_succeeded...................: 100.00% 381 out of 381
    checks_failed......................: 0.00%   0 out of 381

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=10.27s min=599.3ms med=10.88s max=17.59s p(90)=16.32s p(95)=16.58s
      { expected_response:true }............................................: avg=10.27s min=599.3ms med=10.88s max=17.59s p(90)=16.32s p(95)=16.58s
    http_req_failed.........................................................: 0.00%  0 out of 381
    http_reqs...............................................................: 381    2.838553/s

    EXECUTION
    iteration_duration......................................................: avg=31.07s min=2.86s   med=33.17s max=48.56s p(90)=46.69s p(95)=47.35s
    iterations..............................................................: 120    0.894032/s
    vus.....................................................................: 3      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 1.0 MB 7.5 kB/s
    data_sent...............................................................: 75 kB  561 B/s




running (2m14.2s), 00/50 VUs, 120 complete and 9 interrupted iterations
default ✓ [======================================] 00/50 VUs  2m0s



| **Métrique**          | **2 instances** | **3 instances** |
| --------------------- | --------------- | --------------- |
| **Trafic total**      |                 |                 |
| **Erreurs (nb)**      |                 |                 |
| **Réponses**          |                 |                 |
| **Latence P95 & P99** |                 |                 |
| **CPU**               |                 |                 |
| **Mémoire Django**    |                 |                 |





## Lancement du load-test-2.js : 

![alt text](<Capture d’écran 2025-06-29 221516.png>)
![alt text](<Capture d’écran 2025-06-29 221705.png>)


TOTAL RESULTS 

    checks_total.......................: 2311   3.401639/s
    checks_succeeded...................: 72.99% 1687 out of 2311
    checks_failed......................: 27.00% 624 out of 2311

    ✗ stock 200
      ↳  71% — ✓ 592 / ✗ 231
    ✗ rapport 200
      ↳  73% — ✓ 567 / ✗ 202
    ✗ update 200
      ↳  73% — ✓ 528 / ✗ 191

    HTTP
    http_req_duration.......................................................: avg=26.51s min=186.47ms med=26.39s max=1m0s   p(90)=53.37s p(95)=1m0s  
      { expected_response:true }............................................: avg=22.33s min=791.89ms med=23.62s max=59.71s p(90)=40.51s p(95)=44.73s
    http_req_failed.........................................................: 27.00% 624 out of 2311
    http_reqs...............................................................: 2311   3.401639/s

    EXECUTION
    iteration_duration......................................................: avg=1m17s  min=8.86s    med=1m23s  max=3m1s   p(90)=2m9s   p(95)=2m24s 
    iterations..............................................................: 719    1.058321/s
    vus.....................................................................: 3      min=3           max=200
    vus_max.................................................................: 200    min=200         max=200

    NETWORK
    data_received...........................................................: 103 MB 151 kB/s
    data_sent...............................................................: 470 kB 691 B/s




running (11m19.4s), 000/200 VUs, 719 complete and 124 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s
ERRO[0680] thresholds on metrics 'http_req_duration, http_req_failed' have been crossed 


| **Métrique**          | **2 instances** | **3 instances** |
| --------------------- | --------------- | --------------- |
| **Trafic total**      |                 |                 |
| **Erreurs (nb)**      |                 |                 |
| **Réponses**          |                 |                 |
| **Latence P95 & P99** |                 |                 |
| **CPU**               |                 |                 |
| **Mémoire Django**    |                 |                 |


  

## avec quatre instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=4


![alt text](<Capture d’écran 2025-06-29 224336.png>)


## LOAD-TEST.JS : 

![alt text](<Capture d’écran 2025-06-29 225718.png>)

![alt text](<Capture d’écran 2025-06-29 225854.png>)

THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=16.9s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 372     2.752839/s
    checks_succeeded...................: 100.00% 372 out of 372
    checks_failed......................: 0.00%   0 out of 372

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=10.47s min=628.52ms med=11.34s max=17.98s p(90)=16.53s p(95)=16.9s 
      { expected_response:true }............................................: avg=10.47s min=628.52ms med=11.34s max=17.98s p(90)=16.53s p(95)=16.9s 
    http_req_failed.........................................................: 0.00%  0 out of 372
    http_reqs...............................................................: 372    2.752839/s

    EXECUTION
    iteration_duration......................................................: avg=31.72s min=2.97s    med=34.43s max=49.6s  p(90)=47.43s p(95)=47.91s
    iterations..............................................................: 119    0.880612/s
    vus.....................................................................: 1      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 993 kB 7.3 kB/s
    data_sent...............................................................: 74 kB  547 B/s




running (2m15.1s), 00/50 VUs, 119 complete and 8 interrupted iterations
default ✓ [======================================] 00/50 VUs  2m0s


| **Métrique**          | **3 instances** | **4 instances** |
| --------------------- | --------------- | --------------- |
| **Trafic total**      |                 |                 |
| **Erreurs (nb)**      |                 |                 |
| **Réponses**          |                 |                 |
| **Latence P95 & P99** |                 |                 |
| **CPU**               |                 |                 |
| **Mémoire Django**    |                 |                 |





## Lancement du load-test-2.js : 


![alt text](<Capture d’écran 2025-06-29 230725.png>)
![alt text](<Capture d’écran 2025-06-29 230933.png>)
![alt text](<Capture d’écran 2025-06-29 231114.png>)


THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=1m0s

    http_req_failed
    ✗ 'rate<0.01' rate=31.84%


  █ TOTAL RESULTS 

    checks_total.......................: 2189   3.194414/s
    checks_succeeded...................: 68.15% 1492 out of 2189
    checks_failed......................: 31.84% 697 out of 2189

    ✗ stock 200
      ↳  66% — ✓ 531 / ✗ 265
    ✗ rapport 200
      ↳  67% — ✓ 489 / ✗ 235
    ✗ update 200
      ↳  70% — ✓ 472 / ✗ 197

    HTTP
    http_req_duration.......................................................: avg=27.58s min=474.74ms med=26.65s max=1m2s   p(90)=57.62s p(95)=1m0s  
      { expected_response:true }............................................: avg=20.92s min=634.81ms med=22.38s max=59.74s p(90)=36.33s p(95)=41.21s
    http_req_failed.........................................................: 31.84% 697 out of 2189
    http_reqs...............................................................: 2189   3.194414/s

    EXECUTION
    iteration_duration......................................................: avg=1m18s  min=8.36s    med=1m22s  max=3m2s   p(90)=2m16s  p(95)=2m30s 
    iterations..............................................................: 666    0.971896/s
    vus.....................................................................: 2      min=2           max=200
    vus_max.................................................................: 200    min=200         max=200

    NETWORK
    data_received...........................................................: 120 MB 175 kB/s
    data_sent...............................................................: 450 kB 656 B/s




running (11m25.3s), 000/200 VUs, 666 complete and 154 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s
ERRO[0687] thresholds on metrics 'http_req_duration, http_req_failed' have been crossed 

| **Métrique**          | **3 instances** | **4 instances** |
| --------------------- | --------------- | --------------- |
| **Trafic total**      |                 |                 |
| **Erreurs (nb)**      |                 |                 |
| **Réponses**          |                 |                 |
| **Latence P95 & P99** |                 |                 |
| **CPU**               |                 |                 |
| **Mémoire Django**    |                 |                 |






## config nginx utilisée 


worker_processes auto;

events {
    worker_connections 1024;
}

http {
    
    resolver 127.0.0.11 valid=30s;

    upstream django_backend {
        zone django_backend 64k;            
        server web:8000 resolve;            
    }

    server {
        listen 80;

        location / {
            proxy_pass         http://django_backend;
            proxy_set_header   Host              $host;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            add_header         X-Served-By       $upstream_addr;
        }

        location /metrics {
            proxy_pass         http://django_backend/metrics;
            proxy_set_header   Host              $host;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        }
    }
}

