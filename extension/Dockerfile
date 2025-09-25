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

# Copy HTML files to root directory (Vite generates them in subdirectories)
RUN if [ -f /app/dist/src/popup/index.html ]; then \
        cp /app/dist/src/popup/index.html /app/dist/popup.html; \
    fi && \
    if [ -f /app/dist/src/options/index.html ]; then \
        cp /app/dist/src/options/index.html /app/dist/options.html; \
    fi && \
    echo "HTML files copied to root directory"

# Create content directory (no CSS files needed since content scripts were removed)
RUN mkdir -p /app/dist/content

# Verify build output
RUN echo "=== DIST ROOT ===" && \
    ls -la /app/dist/ && \
    echo "=== DIST CONTENT ===" && \
    ls -la /app/dist/content/ && \
    echo "=== DIST BACKGROUND ===" && \
    ls -la /app/dist/background/ || true

# Default command - just keep container running
CMD ["tail", "-f", "/dev/null"]