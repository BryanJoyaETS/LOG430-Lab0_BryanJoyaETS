# LOG430-Lab0_BryanJoyaETS

# Laboratoire 0 - Hello World App

Cette application Python affiche le message `"Hello World"`.
Elle est conçue comme un projet de base pour démontrer :

- l'utilisation de tests unitaires
- la containerisation avec Docker
- la mise en place d'une pipeline CI/CD avec GitHub Actions

cloner le projet : git clone https://github.com/BryanJoyaETS/LOG430-Lab0_BryanJoyaETS.git

---

### Exécuter localement

#### Prérequis :
- Python 3.11
- `pip`
- `pylint`
- `pytest`

#### Dans bash :
```text

sudo apt update
sudo apt install python3 python3-pip -y
pip3 install pylint pytest
```
### Structure du projet

```text
LOG430-LAB0BRYANJOYAETS/
├── .github/workflows/ci.yml      # Pipeline CI/CD (GitHub Actions)
├── images/                       # Dossier d'images montrant le bon fonctionnement du projet
├── .dockerignore                 # Fichiers ignorés par Docker
├── .gitignore                    # Fichiers ignorés par Git
├── docker-compose.yml            # Lancement du conteneur
├── Dockerfile                    # Image Docker de l’application
├── hello.py                      # Code principal
├── requirements.txt              # Dépendances Python (pylint, pytest)
├── test_hello.py                 # Test unitaire
└── README.md                     # Ce fichier
```
                  

### Construire et lancer le conteneur :

faire le conteneur : docker-compose up --build

curl http://localhost:5000

fermer le conteneur : docker-compose down

### Captures d'écran

### Création du conteneur

![création du conteneur](/images/image.png)


### Bon fonctionnement du pipeline CI/CD
![pipeline CI/CD](/images/image2.png)



![pipeline CI/CD](/images/image-1.png)



### Bon fonctionnement des test unitaires
![pytest](/images/image3.png)



### Explication de CI/CD


- Job lint :
```text
Utilise Python 3.11

Installe pylint

Analyse le fichier hello.py
```
- Job test :
```text
Utilise Python 3.11

Installe pytest

Exécute test_hello.py
```
- Job build-and-push :
```text
Configure Docker Build

Se connecte à Docker Hub avec des secrets sécurisés de mon dépôt

Construit et pousse l’image vers Docker Hub
```