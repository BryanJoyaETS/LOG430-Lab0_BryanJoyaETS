## avec quatre instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=4


## LOAD-TEST.JS : 

 THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=16.22s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 936     7.700422/s
    checks_succeeded...................: 100.00% 936 out of 936
    checks_failed......................: 0.00%   0 out of 936

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=3.33s  min=6.63ms med=123.38ms max=18.39s p(90)=13.42s p(95)=16.22s
      { expected_response:true }............................................: avg=3.33s  min=6.63ms med=123.38ms max=18.39s p(90)=13.42s p(95)=16.22s
    http_req_failed.........................................................: 0.00%  0 out of 936
    http_reqs...............................................................: 936    7.700422/s

    EXECUTION
    iteration_duration......................................................: avg=10.99s min=1.65s  med=11.26s   max=19.62s p(90)=18.19s p(95)=18.77s
    iterations..............................................................: 312    2.566807/s
    vus.....................................................................: 1      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 2.5 MB 21 kB/s
    data_sent...............................................................: 182 kB 1.5 kB/s




running (2m01.6s), 00/50 VUs, 312 complete and 0 interrupted iterations

| **Métrique**          | **3 instances** | **4 instances** |
| --------------------- | --------------- | --------------- |
| **Trafic total**      |                 |                 |
| **Erreurs (nb)**      |                 |                 |
| **Réponses**          |                 |                 |
| **Latence P95 & P99** |                 |                 |
| **CPU**               |                 |                 |
| **Mémoire Django**    |                 |                 |





## Lancement du load-test-2.js : 



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


