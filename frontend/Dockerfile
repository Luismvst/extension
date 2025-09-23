# Multi-stage build for React frontend
FROM node:20-alpine as deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies
RUN npm install

# Copy source code
COPY . .

# Accept build-time argument for API URL
ARG VITE_API_URL=http://localhost:8080
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine as production

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Copy built application
COPY --from=build /app/dist ./dist

# Expose port
EXPOSE 3000

# Serve the built application
CMD ["serve", "-s", "dist", "-l", "3000"]
