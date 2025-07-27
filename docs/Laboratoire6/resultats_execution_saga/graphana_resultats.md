log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ # Variables
export MAG=101
export PROD=501
export QTY=3
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ docker compose exec -T -e MAG="$MAG" -e PROD="$PROD" stocks python manage.py shell <<'PY'
import os
from stocks.models import Magasin, Produit, Stock
MAG, PROD = int(os.environ["MAG"]), int(os.environ["PROD"])
m,_ = Magasin.objects.get_or_create(id=MAG, defaults={"nom":"MagTest","adresse":"Rue A"})
p,_ = Produit.objects.get_or_create(id=PROD, defaults={"nom":"Chaise","prix":39.99})
Stock.objects.update_or_create(magasin=m, produit=p, defaults={"quantite":15})
print("OK stocks:", m.id, p.id)
PY
OK stocks: 101 501
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ docker compose exec -T -e MAG="$MAG" produits python manage.py shell -c \
"from produits.models import Magasin; Magasin.objects.get_or_create(id=$MAG, defaults={'nom':'MagTest','adresse':'Rue A'})"
docker compose exec -T -e PROD="$PROD" produits python manage.py shell -c \
"from produits.models import Produit; Produit.objects.get_or_create(id=$PROD, defaults={'nom':'Chaise','prix':39.99})"
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ CART=$(docker compose exec -T -e MAG="$MAG" -e PROD="$PROD" -e QTY="$QTY" carts python manage.py shell <<'PY'
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
CART=d8aa013b-8872-4047-809b-5af67c81b35c
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ curl -sS -X POST "http://localhost:8000/api/orchestrator/" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: hp-1" \
  -d "{\"cart_id\":\"$CART\",\"magasin_id\":$MAG}"
echo
{"saga_id":"135b1db9-ffc0-4c62-bb18-5e2a99dfe239","vente_id":5}
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ # Forcer un stock insuffisant
docker compose exec -T stocks python manage.py shell -c \
"from stocks.models import Stock; s=Stock.objects.get(produit_id=$PROD, magasin_id=$MAG); s.quantite=1; s.save(); print('stock=', s.quantite)"
stock= 1
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ CART_FAIL=$(docker compose exec -T -e MAG="$MAG" -e PROD="$PROD" carts python manage.py shell <<'PY'
import os, uuid, sys
from carts.models import Cart, CartLine, Produit
MAG, PROD = int(os.environ["MAG"]), int(os.environ["PROD"])
cart = Cart.objects.create(id=uuid.uuid4(), magasin_id=MAG)
CartLine.objects.create(cart=cart, produit_id=PROD, quantite=2)
sys.stdout.write(str(cart.id))
PY
)
echo "CART_FAIL=$CART_FAIL"
CART_FAIL=7e6ad27c-82b5-436e-bf70-2fc90dc16779
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ curl -sS -X POST "http://localhost:8000/api/orchestrator/" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: rb-1" \
  -d "{\"cart_id\":\"$CART_FAIL\",\"magasin_id\":$MAG}" || true
echo
{"error":"500 Server Error: Internal Server Error for url: http://stocks:8000/api/stock/reservations/"}
log430@log430-etudiante-36:~/LOG430-Lab0_BryanJoyaETS$ 

![alt text](<Capture d’écran 2025-07-26 233547.png>)
![alt text](<Capture d’écran 2025-07-26 232845.png>) 
![alt text](<Capture d’écran 2025-07-26 233147.png>)
