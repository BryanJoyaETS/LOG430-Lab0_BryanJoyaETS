# LOG430-Lab0_BryanJoyaETS

## Laboratoire 3 — Exposition d'une API RESTful pour un système multi-magasins

> **Note :** Le fichier de documentation principal se trouve dans  
> [`docs/Laboratoire3/README.md`](docs/Laboratoire3/README.md)

---

## Exécution du projet

```bash
docker compose -p lab3 build --no-cache
docker compose -p lab3 up -d db
RUN_TESTS=false docker compose -p lab3 up
```

Une fois l'application démarrée, se rendre à l'adresse :  
[http://10.194.32.198:8000](http://10.194.32.198:8000)

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
---

bnp test