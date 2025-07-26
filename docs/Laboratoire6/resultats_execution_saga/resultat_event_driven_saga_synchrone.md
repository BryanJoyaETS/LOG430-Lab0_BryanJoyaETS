# Saga orchestrée — Explication des captures (avec images)

Ce document explique, **capture par capture**, comment ta saga orchestrée synchrone fonctionne, ce que chaque image montre, et **ce que cela prouve** (happy‑path, idempotence, rollback/compensation, traçabilité).

---

## 1) Début de la séquence de tests
![Début tests](<Capture d’écran 2025-07-26 161747.png>)

**Contexte :** sortie terminale / premier retour d’une commande de test.  
**Ce que ça montre :** début de la séquence (environnement prêt).  

---

## 2) Seed côté *stocks*
![Stocks seed](<Capture d’écran 2025-07-26 161808.png>)

**Contexte :** initialisation **stocks**.  
**Ce que ça montre :** *Magasin* `101`, *Produit* `501`, **stock=15**.  
**Ce que ça prouve :** état initial correct.

---

## 3) Seed côté *produits* + création du panier
![Produits + panier](<Capture d’écran 2025-07-26 161821.png>)

**Contexte :** synchronization **produits** + **carts**.  
**Ce que ça montre :** magasin/produit présents dans *produits* ; création **CART=<uuid>** avec **QTY=3**.  
**Ce que ça prouve :** données cohérentes dans les 3 services avant la saga.

---

## 4) Appel de la saga (happy‑path) + événements orchestrateur
![POST orchestrator + events](<Capture d’écran 2025-07-26 161849.png>)

**Contexte :** **POST `/api/orchestrator/`** avec `Idempotency-Key: hp-1`.  
**Ce que ça montre :** réponse avec **`saga_id`** et **`vente_id=1`** ; journal `COMMANDE_CREEE → PANIER_VERROUILLE → STOCK_RESERVE → VENTE_CREEE → TERMINEE`.  
**Ce que ça prouve :** la machine d’états progresse correctement jusqu’à `DONE`.

---

## 5) Effets de bord (stocks & produits)
![Effets de bord](<Capture d’écran 2025-07-26 161928.png>)

**Contexte :** vérifications.  
**Ce que ça montre :** *stocks* : **15 − 3 = 12** ; *produits* : **Vente#1** avec la ligne `{produit_id:501, quantite:3, prix_unitaire:0.00}`.  
**Ce que ça prouve :** effets persistés et cohérents. (*Amélioration : propager `prix_unit` réel depuis carts*.)

---

## 6) Idempotence (rejeu même clé)
![Idempotence](<Capture d’écran 2025-07-26 162124.png>)

**Contexte :** rejouer avec **Idempotency‑Key: hp-1**.  
**Ce que ça montre :** `ventes_avant=1`, `ventes_apres=1`.  
**Ce que ça prouve :** pas de doublon → idempotence côté orchestrateur.

---

## 7) Préparation rollback (échec contrôlé)
![Préparation rollback](<Capture d’écran 2025-07-26 162210.png>)

**Contexte :** **stock=1**, panier **Q=2**, `Idempotency-Key: rb-1`.  
**Ce que ça montre :** conditions réunies pour échec de réservation.  
**Ce que ça prouve :** prêt à valider les compensations.

---

## 8) Résultat rollback (FAILED + compensations)
![Rollback résultat](<Capture d’écran 2025-07-26 162254.png>)

**Contexte :** après l’appel saga en échec.  
**Ce que ça montre :** orchestrateur **`state='FAILED'`** (erreur `/api/stock/reservations/`) ; **cart = OPEN** ; **stock = 1** inchangé.  
**Ce que ça prouve :** **UNLOCK** exécuté, aucun effet de bord persistant côté *produits*, pas de décrément de stock.

---

## 9) Logs *produits* (happy‑path)
![Logs produits](<Capture d’écran 2025-07-26 162315.png>)

**Contexte :** serveur *produits*.  
**Ce que ça montre :** `POST /api/produits/ventes/` → **201**.  
**Ce que ça prouve :** vente créée sur le chemin nominal.

---

## 10) Logs *carts* (lock/unlock)
![Logs carts](<Capture d’écran 2025-07-26 162336.png>)

**Contexte :** serveur *carts*.  
**Ce que ça montre :** `POST /lock/` → **200** (début) ; `POST /unlock/` → **204** (compensation).  
**Ce que ça prouve :** verrouillage/déverrouillage au bon moment.

---

## 11) Logs *stocks* (reservation 201 / 500)
![Logs stocks](<Capture d’écran 2025-07-26 162415.png>)

**Contexte :** serveur *stocks*.  
**Ce que ça montre :** `POST /reservations/` → **201** (happy‑path) ; **500** avec `ValueError("Stock insuffisant")` (rollback).  
**Ce que ça prouve :** la réservation reflète l’état du stock et l’échec est bien remonté.

---

## 12) Logs *orchestrator* (201 + 500)
![Logs orchestrator](<Capture d’écran 2025-07-26 162506.png>)

**Contexte :** serveur orchestrateur.  
**Ce que ça montre :** un `400` (requête invalide), un `201` (happy‑path), un `500` (rollback).  
**Ce que ça prouve :** persistance de `state`/`last_error` et réponses HTTP adaptées.

---

## 13) ServiceEvent par microservice
![ServiceEvent](<Capture d’écran 2025-07-26 164307.png>)

**Contexte :** lecture des événements applicatifs.  
**Ce que ça montre :**  
- **carts** : `LOCK_CART` (SUCCESS), `UNLOCK_CART` (SUCCESS) selon le scénario.  
- **stocks** : `CREATE_RESERVATION` (SUCCESS/FAILURE).  
- **produits** : `CREATE_VENTE` (SUCCESS) en happy‑path.  
**Ce que ça prouve :** **publication d’événements métier** et traçabilité par service.

---

### Synthèse
- **Orchestration synchrone** : `LOCK → RESERVE → CREATE VENTE`, avec événements `SagaEvent` (`COMMANDE_CREEE … TERMINEE/FAILED`).  
- **Idempotence** : pas de doublons.  
- **Rollback/compensation** : UNLOCK panier, pas d’état incohérent.  
- **Traçabilité** : `ServiceEvent` (carts/stocks/produits) + `SagaEvent` (orchestrateur).

> Vers un **event‑driven asynchrone** complet : publier ces événements sur un **bus** (Kafka/RabbitMQ/Redis Streams) et faire réagir les services comme **consumers**.
