import http from 'k6/http';
import { check, sleep } from 'k6';
import encoding from 'k6/encoding';

const BASE = 'http://10.194.32.198:8000/api';
const USER = 'username';
const PASS = 'password';
const authHeader = `Basic ${encoding.b64encode(`${USER}:${PASS}`)}`;

export const options = {
  vus: 200,
  duration: '60s',
  thresholds: {
    http_req_failed: ['rate<0.01'],   
    http_req_duration: ['p(95)<500'],   
  },
};

export default function () {
  const produitId = 1;
  const url = `${BASE}/produit/${produitId}/modifier/?format=json`;

  const payload = JSON.stringify({
    nom:       'Product1',
    categorie: 'Category1',
    prix:      '100.01',
  });

  const params = {
    headers: {
      Authorization: authHeader,
      'Content-Type': 'application/json',
    },
  };

  const res = http.put(url, payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(0.05);
}