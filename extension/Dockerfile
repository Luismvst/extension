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

# Copy built files to dist directory
RUN cp -r dist/* /app/dist/ || true

# Copy CSS files manually
RUN mkdir -p /app/dist/content && \
    if [ -f /app/dist/assets/styles-*.css ]; then \
        cp /app/dist/assets/styles-*.css /app/dist/content/styles.css; \
    else \
        cp src/content/styles.css /app/dist/content/styles.css; \
    fi

# Expose port for development server (optional)
EXPOSE 3000

# Default command
CMD ["npm", "run", "build"]