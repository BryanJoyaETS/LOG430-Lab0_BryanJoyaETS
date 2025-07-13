import http from "k6/http";
import { sleep, check } from "k6";

export let options = {
  stages: [
    { duration: "30s", target: 20 },
    { duration: "60s", target: 50 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<20000"],
    http_req_failed: ["rate<0.10"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost:8000/api";

export default function () {
  const params = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  let res1 = http.get(`${BASE}/stock/1/`, params);
  check(res1, { "stock 200": (r) => r.status === 200 });

  let res2 = http.get(`${BASE}/rapport/ventes/`, params);
  check(res2, { "rapport ventes 200": (r) => r.status === 200 });

  sleep(1);
}
