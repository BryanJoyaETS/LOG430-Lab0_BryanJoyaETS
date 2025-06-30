## avec quatre instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=4


## LOAD-TEST.JS : 

![alt text](<Capture d’écran 2025-06-29 232618.png>)

THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=16.81s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 372     2.793354/s
    checks_succeeded...................: 100.00% 372 out of 372
    checks_failed......................: 0.00%   0 out of 372

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=10.42s min=617.58ms med=11s    max=17.23s p(90)=16.49s p(95)=16.81s
      { expected_response:true }............................................: avg=10.42s min=617.58ms med=11s    max=17.23s p(90)=16.49s p(95)=16.81s
    http_req_failed.........................................................: 0.00%  0 out of 372
    http_reqs...............................................................: 372    2.793354/s

    EXECUTION
    iteration_duration......................................................: avg=31.49s min=2.91s    med=33.56s max=48.5s  p(90)=47.46s p(95)=47.81s
    iterations..............................................................: 118    0.886064/s
    vus.....................................................................: 3      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 993 kB 7.5 kB/s
    data_sent...............................................................: 74 kB  555 B/s




running (2m13.2s), 00/50 VUs, 118 complete and 9 interrupted iterations
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

![alt text](<Capture d’écran 2025-06-29 233323.png>)
![alt text](<Capture d’écran 2025-06-29 233715.png>)

THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=1m3s

    http_req_failed
    ✗ 'rate<0.01' rate=34.88%


  █ TOTAL RESULTS 

    checks_total.......................: 2078   3.016641/s
    checks_succeeded...................: 65.49% 1361 out of 2078
    checks_failed......................: 34.50% 717 out of 2078

    ✗ stock 200
      ↳  66% — ✓ 497 / ✗ 256
    ✗ rapport 200
      ↳  67% — ✓ 467 / ✗ 227
    ✗ update 200
      ↳  62% — ✓ 397 / ✗ 234

    HTTP
    http_req_duration.......................................................: avg=28.26s min=0s    med=26.23s max=1m43s p(90)=59.99s p(95)=1m3s  
      { expected_response:true }............................................: avg=19.02s min=1.21s med=19.26s max=1m18s p(90)=33.53s p(95)=35.95s
    http_req_failed.........................................................: 34.88% 729 out of 2090
    http_reqs...............................................................: 2090   3.034061/s

    EXECUTION
    iteration_duration......................................................: avg=1m19s  min=9.84s med=1m23s  max=3m26s p(90)=2m27s  p(95)=2m50s 
    iterations..............................................................: 629    0.913122/s
    vus.....................................................................: 1      min=1           max=199
    vus_max.................................................................: 200    min=200         max=200

    NETWORK
    data_received...........................................................: 117 MB 170 kB/s
    data_sent...............................................................: 428 kB 621 B/s




running (11m28.8s), 000/200 VUs, 629 complete and 156 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s

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
        least_conn;                     
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


