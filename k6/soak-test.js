import http from "k6/http";
import { sleep, check } from "k6";
import encoding from "k6/encoding";

export let options = {
  vus: 10,
  duration: "30m",
  thresholds: {
    http_req_duration: ["p(95)<1000"], 
    http_req_failed:   ["rate<0.02"],   
  },
};

const BASE = "http://10.194.32.198:8000/api";
const USER = "username";
const PASS = "password";
const authHeader = `Basic ${encoding.b64encode(`${USER}:${PASS}`)}`;
const params = {
  headers: {
    Authorization: authHeader,
    "Content-Type":  "application/json",
  },
};

export default function () {
  let r1 = http.get(`${BASE}/stock/1/`, params);
  check(r1, { "stock 200": (r) => r.status === 200 });

  let r2 = http.get(`${BASE}/rapport/`, params);
  check(r2, { "rapport 200": (r) => r.status === 200 });

  let payload = JSON.stringify({
    nom:       "Product1",
    categorie: "Category1",
    prix:      "100.01",
  });
  let r3 = http.put(
    `${BASE}/produit/1/modifier/?format=json`,
    payload,
    params
  );
  check(r3, { "update 200": (r) => r.status === 200 });

  sleep(1);
}