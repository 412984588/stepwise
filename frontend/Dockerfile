# Frontend Dockerfile for StepWise (React/Vite)
# Multi-stage build: build static assets, then serve with nginx

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build argument for API URL (set at build time)
ARG VITE_API_BASE_URL=https://stepwise-backend-staging.fly.dev
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the application
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 8080

# Health check (use 127.0.0.1 to force IPv4)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/ || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
