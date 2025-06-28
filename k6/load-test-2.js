import http from "k6/http";
import { check, sleep } from "k6";
import encoding from "k6/encoding";

const BASE = "http://10.194.32.198:8000/api";
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
  http.get(`${BASE}/stock/1/`, params);
  http.get(`${BASE}/rapport/`, params);
  http.put(`${BASE}/produit/1/modifier/?format=json`,
           JSON.stringify({ nom: "Product1", categorie: "Category1", prix: "100.01" }),
           params);
  sleep(1);
}