FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY extension/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY extension/ .

# Build the extension
RUN npm run build

# The built extension will be in /app/dist