# Multi-stage Dockerfile for Chrome Extension MV3
FROM node:20-alpine AS base
RUN apk add --no-cache bash git ca-certificates
WORKDIR /app

# Dependencies stage
FROM base AS deps
COPY package*.json ./
RUN npm ci --only=production --frozen-lockfile

# Build stage
FROM base AS build
COPY package*.json ./
RUN npm ci --frozen-lockfile
COPY . .
RUN npm run clean
RUN npm run typecheck
RUN npm run lint
RUN npm run test:unit
RUN npm run build

# E2E stage
FROM mcr.microsoft.com/playwright:v1.40.0-focal AS e2e
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/package*.json ./
COPY --from=build /app/playwright.config.ts ./
COPY --from=build /app/tests ./tests
RUN npm ci --frozen-lockfile
RUN npm run test:e2e

# Artifact stage
FROM base AS artifact
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
RUN npm run package:zip
CMD ["sh", "-c", "ls -la /app/out/"]
