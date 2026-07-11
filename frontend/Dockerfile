# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package requirements
COPY package.json package-lock.json ./
RUN npm ci

# Copy remaining source code and compile
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy reverse-proxy and routes configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
