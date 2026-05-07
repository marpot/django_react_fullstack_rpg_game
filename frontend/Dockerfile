# Etap budowania aplikacji
FROM node:16-alpine AS build

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików konfiguracyjnych
COPY package.json package-lock.json ./

# Instalacja zależności
RUN npm install && npm cache clean --force

# Kopiowanie reszty plików aplikacji
COPY . .

# Budowanie aplikacji
RUN npm run build

# Etap serwowania aplikacji
FROM nginx:alpine

# Kopiowanie zbudowanej aplikacji do katalogu serwera Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Usuwanie domyślnego konfiguratora Nginx (jeśli nie jest potrzebny)
RUN rm /etc/nginx/conf.d/default.conf

# Eksponowanie portu 80
EXPOSE 80

# Uruchomienie Nginx
CMD ["nginx", "-g", "daemon off;"]
