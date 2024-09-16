# app/Dockerfile

FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-it.sh script
COPY wait-for-it.sh /backend/
# Ensure the script is executable
RUN chmod +x /backend/wait-for-it.sh

# Copy the rest of the application code
COPY . /backend

# Copier le reste des fichiers de l'application
COPY . .

# Démarrer le script Python après avoir attendu que Kafka soit prêt
CMD ["./wait-for-it.sh", "kafka:9092", "--", "python", "websocket_bitcoin.py"]
