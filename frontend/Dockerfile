# ── Etapa 1: build ────────────────────────────────────────────────────────────
# Usamos una imagen Node para compilar el frontend con Vite.
# Esta etapa no llega a la imagen final — solo nos importan los archivos de dist/.
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --silent

COPY . .
RUN npm run build
# → genera /app/dist/ con los archivos estáticos optimizados


# ── Etapa 2: serve ────────────────────────────────────────────────────────────
# Imagen final: nginx ligero (~25 MB) que sirve los estáticos y hace proxy al backend.
FROM nginx:alpine

# Copiamos los estáticos desde la etapa de build
COPY --from=builder /app/dist /usr/share/nginx/html

# Reemplazamos la config de nginx por la nuestra
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
