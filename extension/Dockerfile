FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the extension
RUN npm run build

# Expose port for development server (optional)
EXPOSE 3000

# Default command
CMD ["npm", "run", "build"]