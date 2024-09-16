# backend/Dockerfile

FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /backend

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script wait-for-it.sh
COPY wait-for-it.sh .

# Rendre le script exécutable
RUN chmod +x wait-for-it.sh
# Copier le reste des fichiers de l'application
COPY . .

# Exposer le port 8000 pour le backend
EXPOSE 8000

# Démarrer l'application FastAPI avec Uvicorn
CMD ["./wait-for-it.sh", "kafka:9092", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]