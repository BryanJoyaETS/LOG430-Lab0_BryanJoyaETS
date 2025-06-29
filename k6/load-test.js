import http from "k6/http";
import { sleep, check } from "k6";
import encoding from "k6/encoding";

export let options = {
  stages: [
    { duration: "30s", target: 20 },
    { duration: "60s", target: 50 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
  http_req_duration: ["p(95)<20000"],
  http_req_failed:   ["rate<0.10"],
},

};

const BASE = __ENV.BASE_URL || "http://localhost:8000/api";
const USER = "username";
const PASS = "password";

const credentials = `${USER}:${PASS}`;
const authHeader = `Basic ${encoding.b64encode(credentials)}`;

export default function () {
  const params = {
    headers: {
      Authorization: authHeader,
      "Content-Type":  "application/json",
    },
  };

  // 1. Consultation du stock du magasin #1
  let res1 = http.get(`${BASE}/stock/1/`, params);
  check(res1, { "stock 200": (r) => r.status === 200 });

  // 2. Génération du rapport consolidé
  let res2 = http.get(`${BASE}/rapport/`, params);
  check(res2, { "rapport 200": (r) => r.status === 200 });

  // 3. Mise à jour d’un produit #1
  const payload = JSON.stringify({
    nom:       "Product1",
    categorie: "Category1",
    prix:      "100.01",
  });

  
  // on inclut ?format=json dans l’URL
  let res3 = http.put(
    `${BASE}/produit/1/modifier/?format=json`,
    payload,
    params
  );
  check(res3, { "update 200": (r) => r.status === 200 });

  sleep(1);

}