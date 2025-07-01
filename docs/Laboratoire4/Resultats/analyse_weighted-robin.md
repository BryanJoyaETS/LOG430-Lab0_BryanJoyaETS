## avec quatre instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=4


## LOAD-TEST.JS : 

![alt text](<Capture d’écran 2025-06-30 180348.png>)
![alt text](<Capture d’écran 2025-06-30 180420.png>)


 THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<20000' p(95)=34.5s

    http_req_failed
    ✓ 'rate<0.10' rate=0.00%


  █ TOTAL RESULTS 

    checks_total.......................: 372     2.77138/s
    checks_succeeded...................: 100.00% 372 out of 372
    checks_failed......................: 0.00%   0 out of 372

    ✓ stock 200
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=10.31s min=609.06ms med=1.31s  max=36.15s p(90)=32.89s p(95)=34.5s
      { expected_response:true }............................................: avg=10.31s min=609.06ms med=1.31s  max=36.15s p(90)=32.89s p(95)=34.5s
    http_req_failed.........................................................: 0.00%  0 out of 372
    http_reqs...............................................................: 372    2.77138/s

    EXECUTION
    iteration_duration......................................................: avg=30.75s min=3.01s    med=30.78s max=1m24s  p(90)=1m2s   p(95)=1m4s 
    iterations..............................................................: 119    0.886544/s
    vus.....................................................................: 3      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 992 kB 7.4 kB/s
    data_sent...............................................................: 74 kB  551 B/s




running (2m14.2s), 00/50 VUs, 119 complete and 9 interrupted iterations
default ✓ [======================================] 00/50 VUs  2m0s
ERRO[0135] thresholds on metrics 'http_req_duration' have been crossed 


## Lancement du load-test-2.js : 

![alt text](<Capture d’écran 2025-06-30 181537.png>)
![alt text](<Capture d’écran 2025-06-30 182142.png>)

█ THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=1m0s

    http_req_failed
    ✗ 'rate<0.01' rate=34.75%


  █ TOTAL RESULTS 

    checks_total.......................: 2345   3.448903/s
    checks_succeeded...................: 65.24% 1530 out of 2345
    checks_failed......................: 34.75% 815 out of 2345

    ✗ stock 200
      ↳  64% — ✓ 533 / ✗ 298
    ✗ rapport 200
      ↳  65% — ✓ 515 / ✗ 270
    ✗ update 200
      ↳  66% — ✓ 482 / ✗ 247

    HTTP
    http_req_duration.......................................................: avg=26.17s min=185.34ms med=23.53s max=1m0s   p(90)=1m0s   p(95)=1m0s  
      { expected_response:true }............................................: avg=18.37s min=667.6ms  med=10.81s max=59.88s p(90)=47.59s p(95)=53.64s
    http_req_failed.........................................................: 34.75% 815 out of 2345
    http_reqs...............................................................: 2345   3.448903/s

    EXECUTION
    iteration_duration......................................................: avg=1m16s  min=3.6s     med=1m19s  max=3m1s   p(90)=2m19s  p(95)=2m33s 
    iterations..............................................................: 727    1.069233/s
    vus.....................................................................: 1      min=1           max=200
    vus_max.................................................................: 200    min=200         max=200

    NETWORK
    data_received...........................................................: 107 MB 157 kB/s
    data_sent...............................................................: 476 kB 700 B/s




running (11m19.9s), 000/200 VUs, 727 complete and 121 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s
ERRO[0680] thresholds on metrics 'http_req_duration, http_req_failed' have been crossed 


## config nginx utilisée 

worker_processes auto;

events {
    worker_connections 1024;
}

http {
    resolver 127.0.0.11 valid=30s;

    upstream django_backend {
        zone django_backend 64k;

        server lab3-web-1:8000 resolve weight=4;
        server lab3-web-2:8000 resolve weight=2;
        server lab3-web-3:8000 resolve weight=2;
        server lab3-web-4:8000 resolve weight=1;
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


