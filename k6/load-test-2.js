import http from "k6/http";
import { check, sleep } from "k6";
import encoding from "k6/encoding";

const BASE = __ENV.BASE_URL || "http://localhost:8000/api";
const authHeader = `Basic ${encoding.b64encode(`username:password`)}`;
const params = {
  headers: {
    Authorization: authHeader,
    "Content-Type": "application/json",
  },
};

export let options = {
  scenarios: {
    stress: {
      executor: "ramping-vus",
      startVUs: 10,
      stages: [
        { duration: "2m", target: 20 },   
        { duration: "3m", target: 100 },  
        { duration: "4m", target: 200 },  
        { duration: "2m", target: 0 },   
      ],
      gracefulRampDown: "30s",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

export default function () {
  // Requête 1 - stock
  let res1 = http.get(`${BASE}/stock/1/`, params);
  console.log(`Stock served by: ${res1.headers["X-Served-By"] || "unknown"}`);
  check(res1, { "stock 200": (r) => r.status === 200 });

  // Requête 2 - rapport
  let res2 = http.get(`${BASE}/rapport/`, params);
  console.log(`Rapport served by: ${res2.headers["X-Served-By"] || "unknown"}`);
  check(res2, { "rapport 200": (r) => r.status === 200 });

  // Requête 3 - update produit
  let payload = JSON.stringify({ nom: "Product1", categorie: "Category1", prix: "100.01" });
  let res3 = http.put(`${BASE}/produit/1/modifier/?format=json`, payload, params);
  console.log(`Update served by: ${res3.headers["X-Served-By"] || "unknown"}`);
  check(res3, { "update 200": (r) => r.status === 200 });

  sleep(1);
}
