# LOG430-Lab0_BryanJoyaETS

## Laboratoire 6 — Implémentation d'une saga orchestrée et gestion de la machine d'état

> **Note :** Le fichier de documentation principal se trouve dans  
> [`docs/Laboratoire6/README.md`](../Laboratoire6/README.md)

---

# Saga Orchestrée – Laboratoire 6

## Résumé  
Ce laboratoire met en place une **saga orchestrée synchrone** pour la création d’une commande, impliquant 3 microservices : **carts**, **stocks**, **produits** et un **orchestrateur** central.  
Flux métier : **LOCK cart → RESERVE stock → CREATE vente → DONE** (ou **compensation** en cas d’échec).

Le système persiste les **états** (`Saga`, `SagaEvent`), journalise des **événements** de service (`ServiceEvent`) et expose des **métriques Prometheus** visualisables dans **Grafana**.

---
## Objectifs  
 — Comprendrele concept de Saga orchestrée synchrone pour la gestion des transactions
 distribuées.
 — Implémenter une orchestration centralisée et synchrone entre 3 à 4 microservices.
 — Mettre en place un suivi de la machine d’état d’une entité métier (par exemple :
 Commande).
 — Gérer les événements métiers, les échecs partiels et les compensations.

## Exécution du projet

```bash
docker compose build --no-cache
RUN_TESTS=false docker compose  up -d
```
---
Une fois l'application démarrée, se rendre à l'adresse pour le site principal:  
[http://localhost:8000](http://localhost:8000)

Mon dashboard Graphana :
[http://localhost:3000/dashboards](http://localhost:3000/dashboards)

Mon scraping Prometheus :

Les targets : [http://10.194.32.198:9090/targets](http://10.194.32.198:9090/targets)

ADRs : 

[`docs/Laboratoire6/ADR`](../Laboratoire6/ADR/001.md) ainsi que les autres dans le même dossier


---


## Clonage des laboratoires précédents

- **Laboratoire 0 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab0
- **Laboratoire 1 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab1
- **Laboratoire 2 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab2
- **Laboratoire 3 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab3
- **Laboratoire 4 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab4
- **Laboratoire 5 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab5
- **Laboratoire 6 :**  
  `git clone` https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS/releases/tag/Lab6

---

## Structure du projet : 

- **orchestrator** — DRF, endpoint **`POST /api/orchestrator/`** (lance la saga), persiste `Saga` + `SagaEvent`, expose **`/metrics`**.
- **carts** — lock/unlock panier :
  - `POST /api/caisse/<uuid:cart_id>/lock/`
  - `POST /api/caisse/<uuid:cart_id>/unlock/`
- **stocks** — réservations :
  - `POST /api/stock/reservations/`
  - `DELETE /api/stock/reservations/<uuid:reservation_id>/`
- **produits** — ventes :
  - `POST /api/produits/ventes/`
  - `DELETE /api/produits/ventes/<int:vente_id>/`
- **lb (nginx)** — reverse proxy exposé sur **:8000**
- **db (postgres)** — base
- **prometheus** — scrape des métriques
- **grafana** — visualisation

---


## Analyse des tests et Graphana

```bash

# Variables
export MAG=101
export PROD=501
export QTY=3

# peupler stocks (magasin, produit, stock=15)
docker compose exec -T -e MAG="$MAG" -e PROD="$PROD" stocks python manage.py shell <<'PY'
import os
from stocks.models import Magasin, Produit, Stock
MAG, PROD = int(os.environ["MAG"]), int(os.environ["PROD"])
m,_ = Magasin.objects.get_or_create(id=MAG, defaults={"nom":"MagTest","adresse":"Rue A"})
p,_ = Produit.objects.get_or_create(id=PROD, defaults={"nom":"Chaise","prix":39.99})
Stock.objects.update_or_create(magasin=m, produit=p, defaults={"quantite":15})
print("OK stocks:", m.id, p.id)
PY

# peupler produits (synchroniser magasin & produit)
docker compose exec -T -e MAG="$MAG" produits python manage.py shell -c \
"from produits.models import Magasin; Magasin.objects.get_or_create(id=$MAG, defaults={'nom':'MagTest','adresse':'Rue A'})"

docker compose exec -T -e PROD="$PROD" produits python manage.py shell -c \
"from produits.models import Produit; Produit.objects.get_or_create(id=$PROD, defaults={'nom':'Chaise','prix':39.99})"
```

```bash
# Créer un panier avec QTY=3
CART=$(docker compose exec -T -e MAG="$MAG" -e PROD="$PROD" -e QTY="$QTY" carts python manage.py shell <<'PY'
import os, uuid, sys
from carts.models import Cart, CartLine, Produit
MAG, PROD, QTY = int(os.environ["MAG"]), int(os.environ["PROD"]), int(os.environ["QTY"])
Produit.objects.get_or_create(id=PROD, defaults={"nom":"Chaise","prix":39.99})
cart = Cart.objects.create(id=uuid.uuid4(), magasin_id=MAG)
CartLine.objects.create(cart=cart, produit_id=PROD, quantite=QTY)
sys.stdout.write(str(cart.id))
PY
)
echo "CART=$CART"

# Lancer la saga (idempotency key = hp-1)
curl -sS -X POST "http://localhost:8000/api/orchestrator/" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: hp-1" \
  -d "{\"cart_id\":\"$CART\",\"magasin_id\":$MAG}"
# ⇒ {"saga_id":"<uuid>","vente_id":<int>}

# Vérifier la saga & effets
docker compose exec -T orchestrator python manage.py shell -c \
"from orchestrator.models import Saga; s=Saga.objects.latest('created_at'); \
print({'state': s.state, 'vente_id': s.vente_id, 'reservation_id': s.reservation_id, 'error': s.last_error})"

# Stock attendu : 15 - 3 = 12
docker compose exec -T stocks python manage.py shell -c \
"from stocks.models import Stock; print(Stock.objects.get(produit_id=$PROD, magasin_id=$MAG).quantite)"

# Vente créée
docker compose exec -T produits python manage.py shell -c \
"from produits.models import Vente, LigneVente; v=Vente.objects.latest('date'); \
print({'vente_id': v.id, 'magasin_id': v.magasin_id, 'est_retournee': v.est_retournee}); \
print(list(LigneVente.objects.filter(vente=v).values('produit_id','quantite','prix_unitaire')))"

```
## Attendu : state='DONE', stock décrémenté, vente créée.

```bash
# Rejouer la même requête (même clé hp-1)
curl -sS -X POST "http://localhost:8000/api/orchestrator/" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: hp-1" \
  -d "{\"cart_id\":\"$CART\",\"magasin_id\":$MAG}"

# Compter les ventes (doit rester identique)
docker compose exec -T produits python manage.py shell -c \
"from produits.models import Vente; print('ventes=', Vente.objects.count())"
```

### Attendu : pas de doublon.

```bash

# Stock OK
docker compose exec -T stocks python manage.py shell -c \
"from stocks.models import Stock; s=Stock.objects.get(produit_id=$PROD, magasin_id=$MAG); s.quantite=10; s.save(); print('stock=', s.quantite)"

# Panier Q=2
CART_RB=$(docker compose exec -T -e MAG="$MAG" -e PROD="$PROD" carts python manage.py shell <<'PY'
import os, uuid, sys
from carts.models import Cart, CartLine
MAG, PROD = int(os.environ["MAG"]), int(os.environ["PROD"])
cart = Cart.objects.create(id=uuid.uuid4(), magasin_id=MAG)
CartLine.objects.create(cart=cart, produit_id=PROD, quantite=2)
sys.stdout.write(str(cart.id))
PY
)
echo "CART_RB=$CART_RB"

# Arrêter produits → forcer l’échec en étape 3
docker compose stop produits

# Saga (échec attendu)
curl -sS -X POST "http://localhost:8000/api/orchestrator/" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: rb-propre-1" \
  -d "{\"cart_id\":\"$CART_RB\",\"magasin_id\":$MAG}" || true

# Redémarrer produits
docker compose start produits

# Vérifier compensations
docker compose exec -T orchestrator python manage.py shell -c \
"from orchestrator.models import Saga; s=Saga.objects.latest('created_at'); \
print('state=', s.state, 'error=', s.last_error, 'reservation_id=', s.reservation_id, 'cart_id=', s.cart_id)"

docker compose exec -T -e CART="$CART_RB" carts python manage.py shell -c \
"from carts.models import Cart; import uuid, os; \
c=Cart.objects.get(id=uuid.UUID(os.environ['CART'])); print('cart_status=', c.status)"

docker compose exec -T -e RES_ID="$(docker compose exec -T orchestrator python manage.py shell -c "from orchestrator.models import Saga; print(Saga.objects.latest('created_at').reservation_id)")" \
  stocks python manage.py shell -c \
"from stocks.models import Reservation; import uuid, os; \
r=Reservation.objects.get(id=uuid.UUID(os.environ['RES_ID'])); print('reservation_status=', r.status)"

```
## Attendu : state='FAILED', cart_status=OPEN, stock inchangé (=1).

```bash
# Stock OK
docker compose exec -T stocks python manage.py shell -c \
"from stocks.models import Stock; s=Stock.objects.get(produit_id=$PROD, magasin_id=$MAG); s.quantite=10; s.save(); print('stock=', s.quantite)"

# Panier Q=2
CART_RB=$(docker compose exec -T -e MAG="$MAG" -e PROD="$PROD" carts python manage.py shell <<'PY'
import os, uuid, sys
from carts.models import Cart, CartLine
MAG, PROD = int(os.environ["MAG"]), int(os.environ["PROD"])
cart = Cart.objects.create(id=uuid.uuid4(), magasin_id=MAG)
CartLine.objects.create(cart=cart, produit_id=PROD, quantite=2)
sys.stdout.write(str(cart.id))
PY
)
echo "CART_RB=$CART_RB"

# Arrêter produits → forcer l’échec en étape 3
docker compose stop produits

# Saga (échec attendu)
curl -sS -X POST "http://localhost:8000/api/orchestrator/" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: rb-propre-1" \
  -d "{\"cart_id\":\"$CART_RB\",\"magasin_id\":$MAG}" || true

# Redémarrer produits
docker compose start produits

# Vérifier compensations
docker compose exec -T orchestrator python manage.py shell -c \
"from orchestrator.models import Saga; s=Saga.objects.latest('created_at'); \
print('state=', s.state, 'error=', s.last_error, 'reservation_id=', s.reservation_id, 'cart_id=', s.cart_id)"

docker compose exec -T -e CART="$CART_RB" carts python manage.py shell -c \
"from carts.models import Cart; import uuid, os; \
c=Cart.objects.get(id=uuid.UUID(os.environ['CART'])); print('cart_status=', c.status)"

docker compose exec -T -e RES_ID="$(docker compose exec -T orchestrator python manage.py shell -c "from orchestrator.models import Saga; print(Saga.objects.latest('created_at').reservation_id)")" \
  stocks python manage.py shell -c \
"from stocks.models import Reservation; import uuid, os; \
r=Reservation.objects.get(id=uuid.UUID(os.environ['RES_ID'])); print('reservation_status=', r.status)"

```
## Attendu : state='FAILED', cart_status=OPEN, reservation_status=RELEASED.



## Événements côté orchestrateur

```bash
docker compose exec -T orchestrator python manage.py shell -c \
"from orchestrator.models import Saga, SagaEvent; s=Saga.objects.latest('created_at'); \
print({'id': s.id, 'state': s.state}); print(list(s.events.values('type','payload','created_at')))"
# Happy‑path : COMMANDE_CREEE → PANIER_VERROUILLE → STOCK_RESERVE → VENTE_CREEE → TERMINEE

```

## Événements côté microservices
```bash
# carts
docker compose exec -T carts python manage.py shell -c \
"from carts.models import ServiceEvent; print(list(ServiceEvent.objects.order_by('-created_at')[:10].values('action','outcome','correlation_id','detail')))"

# stocks
docker compose exec -T stocks python manage.py shell -c \
"from stocks.models import ServiceEvent; print(list(ServiceEvent.objects.order_by('-created_at')[:10].values('action','outcome','correlation_id','detail')))"

# produits
docker compose exec -T produits python manage.py shell -c \
"from produits.models import ServiceEvent; print(list(ServiceEvent.objects.order_by('-created_at')[:10].values('action','outcome','correlation_id','detail')))"
```

![alt text](<Capture >) ![alt text](<Capture d’écran 2025-07-26 232845.png>) ![alt text](<Capture d’écran 2025-07-26 233147.png>)