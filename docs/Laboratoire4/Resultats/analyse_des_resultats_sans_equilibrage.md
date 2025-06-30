## avec deux instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=2
[+] Running 7/7
 ✔ Container lab3-k6-1       Started                                                                                                                                                                                                                   1.2s 
 ✔ Container my-postgres-3   Running                                                                                                                                                                                                                   0.0s 
 ✔ Container lab3-web-2      Started                                                                                                                                                                                                                   0.9s 
 ✔ Container prometheus      Started                                                                                                                                                                                                                   1.2s 
 ✔ Container lab3-web-1      Started                                                                                                                                                                                                                   1.5s 
 ✔ Container lab3-lb-1       Started                                                                                                                                                                                                                   2.7s 
 ✔ Container lab3-grafana-1  Started           

## LOAD-TEST.JS : 


![alt text](<captures/Capture d’écran 2025-06-29 160825.png>)


![alt text](<captures/Capture d’écran 2025-06-29 161439.png>)


Répartition du trafic :
lab3-web-1:8000 → 0.758 req/s

lab3-web-2:8000 → 0.754 req/s

 La charge est quasiment égale sur les deux instances : preuve que le load balancer distribue bien les requêtes 

Répartition des réponses :
lab3-web-1 : 227 réponses

lab3-web-2 : 226 réponses

Encore une fois, on voit une parfaite répartition des requêtes.

Charge CPU et mémoire similaires :
CPU : ~44 % sur les deux

Mémoire : ~75 MiB

Les deux services travaillent équitablement.

Latence (P95 & P99) :
Les courbes sont très similaires pour les deux instances.

Cela montre que les deux conteneurs répondent à des charges comparables.


## Lancement du load-test-2.js : 


![alt text](<captures/Capture d’écran 2025-06-29 162458.png>)
![alt text](<captures/Capture d’écran 2025-06-29 164928.png>)
![alt text](<captures/Capture d’écran 2025-06-29 165307.png>)
![alt text](<captures/Capture d’écran 2025-06-29 165554.png>)
Sans load balancer

![alt text](<captures/Capture d’écran 2025-06-28 183113.png>)


| **Métrique**          | **Avant Load Balancer**                         | **Après Load Balancer (2 instances)**                     |
|-----------------------|--------------------------------------------------|-----------------------------------------------------------|
| **Trafic total**      | 3.90 req/s                                       | 2.08 + 2.01 = **4.09 req/s**                              |
| **Erreurs (nb)**      | 581 erreurs / 1171 réponses (**49%**)            | (246 + 133) / (622 + 602) = **379 / 1224 ≈ 30.9%**         |
| **Latence P99**       | ≈ **1 min 5 s**                                   | ≈ **49.5 s**                                              |
| **CPU**               | **134 %** (1 seule instance surchargée)          | 82.9 % + 94.5 % = **177.4 %** sur 2 instances              |
| **Mémoire Django**    | **193 MiB**                                       | 132 + 85.2 = **217.2 MiB** (~stable)                      |


![alt text](<captures/Capture d’écran 2025-06-29 171050.png>)



## avec trois instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=3
[+] Running 8/8
 ✔ Container prometheus      Started                                                                                                                                                                                                                                               0.8s 
 ✔ Container my-postgres-3   Running                                                                                                                                                                                                                                               0.0s 
 ✔ Container lab3-web-3      Started                                                                                                                                                                                                                                               2.3s 
 ✔ Container lab3-web-1      Started                                                                                                                                                                                                                                               0.8s 
 ✔ Container lab3-web-2      Started                                                                                                                                                                                                                                               1.6s 
 ✔ Container lab3-grafana-1  Started                                                                                                                                                                                                                                               1.8s 
 ✔ Container lab3-lb-1       Started                                                                                                                                                                                                                                               3.4s 
 ✔ Container lab3-k6-1       Started    


## LOAD-TEST.JS : 

![alt text](<captures/Capture d’écran 2025-06-29 175823.png>)



| **Métrique**          | **2 instances**                        | **3 instances**                         |
| --------------------- | -------------------------------------- | --------------------------------------- |
| **Trafic total**      | **0.758 + 0.754 = 1.512 req/s**        | **0.516 + 0.519 + 0.519 = 1.554 req/s** |
| **Erreurs (nb)**      | **227 + 226 = 453 réponses**           | **155 + 156 + 156 = 467 réponses**      |
| **Réponses**          | **227 + 226 = 453 réponses**           | **155 + 156 + 156 = 467 réponses**      |
| **Latence P95 & P99** | **P95 ≈ 150 ms, P99 ≈ 300 ms**         | **P95 ≈ 150 ms, P99 ≈ 300 ms**          |
| **CPU**               | **44 % + 44 % = 88 % (total observé)** | **29.8 % + 30.1 % + 30.0 % = 89.9 %**   |
| **Mémoire Django**    | **75 + 75 = 150 MiB**                  | **75 + 75 + 75 = 225 MiB**              |





## Lancement du load-test-2.js : 


![alt text](<captures/Capture d’écran 2025-06-29 180911.png>)
![alt text](<captures/Capture d’écran 2025-06-29 181615.png>)


| **Métrique**          | **2 instances**                                         | **3 instances**                                                      |
|-----------------------|---------------------------------------------------------|----------------------------------------------------------------------|
| **Trafic total**      | 2.08 + 2.01 = 4.09 req/s                                | 1.31 + 1.40 + 1.39 = **4.1 req/s**                                   |
| **Erreurs (nb)**      | (246 + 133) / (622 + 602) = 379 / 1224 ≈ 30.9 %         | (111 + 134 + 122) / (391 + 418 + 413) = **367 / 1222 ≈ 30 %**        |
| **Réponses**          | 622 + 602 = 1224 réponses                               | 391 + 418 + 413 = **1222 réponses**                                  |
| **Latence P95 & P99** | P99 ≈ 49.5 s                                            | P99 ≈ **49.5 s** (courbes presque superposées entre les 3 pods)      |
| **CPU**               | 82.9 % + 94.5 % = 177.4 %                               | 59.6 % + 60 % + 60.1 % = **179.7 %**                                |
| **Mémoire Django**    | 132 MiB + 85.2 MiB = 217.2 MiB                          | 93.2 MiB + 85.9 MiB + 83.0 MiB = **262.1 MiB**                    |

  
**Interprétation**  
- Le throughput global reste équivalent (~4 req/s), mais chaque instance ne traite plus que ~1.36 req/s au lieu de ~2 req/s, libérant ainsi de la capacité CPU (passage de ~90 % à ~60 % par pod).  
- Le taux d’erreur et la latence ne bougent pas, signe que la base de données ou l’application pose la vraie limite, pas Django.  
- La mémoire totale augmente (3 × 108.6 vs 2 × ~108.6), mais la consommation par pod reste stable.


## avec quatre instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=4


## LOAD-TEST.JS : 


![alt text](<captures/Capture d’écran 2025-06-29 190624.png>)

| **Métrique**          | **3 instances**                                  | **4 instances**                                                    |
|-----------------------|--------------------------------------------------|--------------------------------------------------------------------|
| **Trafic total**      | **0.516 + 0.519 + 0.519 = 1.554 req/s**          | **0.396 + 0.396 + 0.393 + 0.393 = 1.578 req/s**                    |
| **Erreurs (nb)**      | **155 + 156 + 156 = 467 réponses**               | **119 + 119 + 118 + 118 = 474 réponses**                           |
| **Réponses**          | **467 réponses**                                 | **474 réponses**                                                   |
| **Latence P95 & P99** | **P95 ≈ 150 ms, P99 ≈ 300 ms**                   | **P95 ≈ 20 s, P99 ≈ 25 s**                                         |
| **CPU**               | **29.8% + 30.1% + 30.0% = 89.9%**                | **22.8% + 22.7% + 22.6% + 22.5% = 90.6%**                          |
| **Mémoire Django**    | **75 + 75 + 75 = 225 MiB**                       | **61.0 + 60.5 + 61.0 + 62.4 = 244.9 MiB**                          |




## Lancement du load-test-2.js : 

| **Métrique**          | **3 instances**                                                      | **4 instances**                                                       |
|-----------------------|----------------------------------------------------------------------|------------------------------------------------------------------------|
| **Trafic total**      | 1.31 + 1.40 + 1.39 = **4.1 req/s**                                   | 1.23 + 1.40 + 1.48 + 1.21 = **5.32 req/s**                              |
| **Erreurs (nb)**      | (111 + 134 + 122) / (391 + 418 + 413) = **367 / 1222 ≈ 30 %**         | (371 + 418 + 255 + 191) / (371 + 418 + 443 + 362) = **1235 / 1594 ≈ 77.5 %** |
| **Réponses**          | 391 + 418 + 413 = **1222 réponses**                                  | 371 + 418 + 443 + 362 = **1594 réponses**                              |
| **Latence P95 & P99** | P99 ≈ **49.5 s** (courbes presque superposées entre les 3 pods)      | P99 ≈ **49.5 s** (courbes presque superposées entre les 4 pods)        |
| **CPU**               | 59.6 % + 60 % + 60.1 % = **179.7 %**                                 | 44.1 % + 44.0 % + 43.8 % + 40.2 % = **172.1 %**                        |
| **Mémoire Django**    | 93.2 MiB + 85.9 MiB + 83.0 MiB = **262.1 MiB**                        | 102 MiB + 77 MiB + 110 MiB + 94.6 MiB = **383.6 MiB**                  |


![alt text](<captures/Capture d’écran 2025-06-29 194544.png>)




config nginx utilisée 


events {}
http {
  upstream django {
    server web:8000;
  }
  server {
    listen 80;
    location / {
      proxy_pass http://django;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Served-By $upstream_addr;
    }
  }
}

## aucune stratégie de load balancing n'est appliquée ici