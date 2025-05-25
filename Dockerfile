FROM python:3.11-slim

WORKDIR /app

# Copier requirements si tu as un fichier requirements.txt
COPY requirements.txt ./

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l’application
COPY . .

CMD ["python", "-m", "application.main"]
