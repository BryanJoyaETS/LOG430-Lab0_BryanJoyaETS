## avec quatre instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=4


## LOAD-TEST.JS : 

![alt text](<Capture d’écran 2025-06-30 191219.png>)

THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=16.74s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 371     2.755484/s
    checks_succeeded...................: 100.00% 371 out of 371
    checks_failed......................: 0.00%   0 out of 371

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=10.5s  min=625.56ms med=11.4s  max=19.13s p(90)=16.4s  p(95)=16.74s
      { expected_response:true }............................................: avg=10.5s  min=625.56ms med=11.4s  max=19.13s p(90)=16.4s  p(95)=16.74s
    http_req_failed.........................................................: 0.00%  0 out of 371
    http_reqs...............................................................: 371    2.755484/s

    EXECUTION
    iteration_duration......................................................: avg=31.64s min=3.06s    med=34.68s max=51.15s p(90)=46.75s p(95)=47.91s
    iterations..............................................................: 117    0.86898/s
    vus.....................................................................: 4      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 996 kB 7.4 kB/s
    data_sent...............................................................: 74 kB  551 B/s




running (2m14.6s), 00/50 VUs, 117 complete and 10 interrupted iterations
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

![alt text](<Capture d’écran 2025-06-30 191927.png>)
![alt text](<Capture d’écran 2025-06-30 192130.png>)

THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=1m0s

    http_req_failed
    ✗ 'rate<0.01' rate=33.12%


  █ TOTAL RESULTS 

    checks_total.......................: 2427   3.548472/s
    checks_succeeded...................: 66.87% 1623 out of 2427
    checks_failed......................: 33.12% 804 out of 2427

    ✗ stock 200
      ↳  64% — ✓ 567 / ✗ 310
    ✗ rapport 200
      ↳  68% — ✓ 553 / ✗ 252
    ✗ update 200
      ↳  67% — ✓ 503 / ✗ 242

    HTTP
    http_req_duration.......................................................: avg=25.49s min=132.31ms med=22.46s max=1m0s   p(90)=1m0s   p(95)=1m0s  
      { expected_response:true }............................................: avg=22.47s min=757.51ms med=21.09s max=59.84s p(90)=45.37s p(95)=50.72s
    http_req_failed.........................................................: 33.12% 804 out of 2427
    http_reqs...............................................................: 2427   3.548472/s

    EXECUTION
    iteration_duration......................................................: avg=1m13s  min=1.46s    med=1m14s  max=3m1s   p(90)=2m13s  p(95)=2m33s 
    iterations..............................................................: 742    1.084865/s
    vus.....................................................................: 1      min=1           max=200
    vus_max.................................................................: 200    min=200         max=200

    NETWORK
    data_received...........................................................: 124 MB 181 kB/s
    data_sent...............................................................: 496 kB 725 B/s




running (11m24.0s), 000/200 VUs, 742 complete and 151 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s
ERRO[0684] thresholds on metrics 'http_req_duration, http_req_failed' have been crossed 


## config nginx utilisée 

worker_processes auto;

events {
    worker_connections 1024;
}

http {
    upstream django_backend {
        ip_hash;

        server lab3-web-1:8000;
        server lab3-web-2:8000;
        server lab3-web-3:8000;
        server lab3-web-4:8000;
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



