## Tolerance aux pannes avec une config least-connection

## avec quatre instances du service API : 
## log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ RUN_TESTS=false docker compose -p lab3 up -d --scale web=4

## LOAD-TEST.JS :


## Avec 4 instances fonctionnelles 

![alt text](<Capture d’écran 2025-06-30 195912.png>)

## Après l'arrêt d'une instance  : 

![alt text](<Capture d’écran 2025-06-30 200047.png>)
![alt text](<Capture d’écran 2025-06-30 200117.png>)

## Après l'arrêt de 2 instances instance : 

![alt text](<Capture d’écran 2025-06-30 200213.png>)

THRESHOLDS 

    http_req_duration
    ✓ 'p(95)<20000' p(95)=19.1s

    http_req_failed
    ✓ 'rate<0.10' rate=0.28%


  █ TOTAL RESULTS 

    checks_total.......................: 353    2.63385/s
    checks_succeeded...................: 99.71% 352 out of 353
    checks_failed......................: 0.28%  1 out of 353

    ✗ stock 200
      ↳  99% — ✓ 120 / ✗ 1
    ✓ rapport 200
    ✓ update 200

    HTTP
    http_req_duration.......................................................: avg=11.05s min=599.65ms med=11.43s max=38.91s p(90)=17.14s p(95)=19.1s 
      { expected_response:true }............................................: avg=10.97s min=599.65ms med=11.39s max=32.08s p(90)=17.04s p(95)=19.02s
    http_req_failed.........................................................: 0.28%  1 out of 353
    http_reqs...............................................................: 353    2.63385/s

    EXECUTION
    iteration_duration......................................................: avg=33.29s min=2.86s    med=35.95s max=1m3s   p(90)=48.09s p(95)=52.78s
    iterations..............................................................: 111    0.828208/s
    vus.....................................................................: 1      min=1        max=50
    vus_max.................................................................: 50     min=50       max=50

    NETWORK
    data_received...........................................................: 942 kB 7.0 kB/s
    data_sent...............................................................: 70 kB  525 B/s




running (2m14.0s), 00/50 VUs, 111 complete and 10 interrupted iterations
default ✓ [======================================] 00/50 VUs  2m0s


## LOAD-TEST-2.JS :

## Avec 4 instances fonctionnelles :

![alt text](<Capture d’écran 2025-06-30 201835.png>)
![alt text](<Capture d’écran 2025-06-30 201913.png>)

## Après l'arrêt d'une instance  : 

![alt text](<Capture d’écran 2025-06-30 202027.png>)
![alt text](<Capture d’écran 2025-06-30 202111.png>)
![alt text](<Capture d’écran 2025-06-30 202139.png>)
![alt text](<Capture d’écran 2025-06-30 202314.png>)

## Après l'arrêt de 2 instances instance : 

![alt text](<Capture d’écran 2025-06-30 202409.png>)
![alt text](<Capture d’écran 2025-06-30 202450.png>)
![alt text](<Capture d’écran 2025-06-30 202519.png>)
![alt text](<Capture d’écran 2025-06-30 202538.png>)

THRESHOLDS 

    http_req_duration
    ✗ 'p(95)<500' p(95)=1m0s

    http_req_failed
    ✗ 'rate<0.01' rate=43.10%


  █ TOTAL RESULTS 

    checks_total.......................: 2960   4.369191/s
    checks_succeeded...................: 56.89% 1684 out of 2960
    checks_failed......................: 43.10% 1276 out of 2960

    ✗ stock 200
      ↳  58% — ✓ 609 / ✗ 429
    ✗ rapport 200
      ↳  56% — ✓ 560 / ✗ 423
    ✗ update 200
      ↳  54% — ✓ 515 / ✗ 424

    HTTP
    http_req_duration.......................................................: avg=20.63s min=332.94µs med=20.13s max=1m0s   p(90)=48.65s p(95)=1m0s  
      { expected_response:true }............................................: avg=22.52s min=635.52ms med=22.84s max=59.96s p(90)=40.78s p(95)=50.01s
    http_req_failed.........................................................: 43.10% 1276 out of 2960
    http_reqs...............................................................: 2960   4.369191/s

    EXECUTION
    iteration_duration......................................................: avg=59.22s min=1s       med=1m3s   max=3m1s   p(90)=2m1s   p(95)=2m15s 
    iterations..............................................................: 937    1.383085/s
    vus.....................................................................: 4      min=4            max=200
    vus_max.................................................................: 200    min=200          max=200

    NETWORK
    data_received...........................................................: 115 MB 169 kB/s
    data_sent...............................................................: 595 kB 878 B/s




running (11m17.5s), 000/200 VUs, 937 complete and 118 interrupted iterations
stress ✓ [======================================] 000/200 VUs  11m0s
ERRO[0677] thresholds on metrics 'http_req_duration, http_req_failed' have been crossed 