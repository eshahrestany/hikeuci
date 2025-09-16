# ---- Build stage: compile Vue into /app/dist
FROM node:22-alpine AS build
WORKDIR /frontend

# Install deps (use npm ci for reproducible builds)
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
# Optionally pass an API base via build-arg; default is /api on same origin
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# ---- Runtime stage: Nginx serves the built assets and proxies /api to Flask
FROM nginx:1.27-alpine

# Copy built static files into standard web root
COPY --from=build /frontend/dist /usr/share/nginx/html

# Nginx config
COPY /nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Prepare mount for uWSGI Unix socket shared with backend
RUN mkdir -p /sock

# (Optional) basic healthcheck file
RUN printf "ok\n" > /usr/share/nginx/html/healthz
