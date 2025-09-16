# ---- Build stage: compile Vue into /frontend/dist
FROM node:22-alpine AS build
WORKDIR /frontend

# These paths are relative to the *build context* (repo root)
COPY frontend/package*.json ./
RUN npm ci

# Copy the Vue source
COPY frontend/ .
ARG VITE_GOOGLE_CLIENT_ID=/api
ENV VITE_GOOGLE_CLIENT_ID=${VITE_GOOGLE_CLIENT_ID}
RUN npm run build

# ---- Runtime stage: Nginx serves the built assets and proxies /api to Flask
FROM nginx:1.27-alpine

# Copy built static files
COPY --from=build /frontend/dist /usr/share/nginx/html

# Copy nginx.conf from repo's ./nginx folder (host path!)
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf


RUN mkdir -p /sock
RUN printf "ok\n" > /usr/share/nginx/html/healthz
