# frontend/Dockerfile

# Étape 1 : Build de l'application React
FROM node:16-alpine as build

WORKDIR /app

# Copier les fichiers package.json et package-lock.json
COPY package.json package-lock.json ./

# Installer les dépendances
RUN npm install

# Copier le reste des fichiers de l'application
COPY . .

# Construire l'application pour la production
RUN npm run build

# Étape 2 : Servir l'application avec Nginx
FROM nginx:stable-alpine

# Copier les fichiers build dans le répertoire par défaut de Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Exposer le port 80 pour Nginx
EXPOSE 80

# Démarrer Nginx
CMD ["nginx", "-g", "daemon off;"]
