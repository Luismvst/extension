FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the extension (without cleaning dist since it's mounted)
RUN npm run build

# Ensure dist directory exists and copy files
RUN mkdir -p /app/dist && \
    cp -r dist/* /app/dist/ || true

# Copy HTML files to root directory (Vite generates them in subdirectories)
RUN if [ -f /app/dist/src/popup/index.html ]; then \
        cp /app/dist/src/popup/index.html /app/dist/popup.html; \
    fi && \
    if [ -f /app/dist/src/options/index.html ]; then \
        cp /app/dist/src/options/index.html /app/dist/options.html; \
    fi && \
    echo "HTML files copied to root directory"

# Copy CSS files to content directory (ensure it exists)
RUN mkdir -p /app/dist/content && \
    if [ -f /app/dist/content/styles.css ]; then \
        echo "CSS already in place"; \
    else \
        cp src/content/styles.css /app/dist/content/styles.css; \
    fi

# Verify build output
RUN echo "=== DIST ROOT ===" && \
    ls -la /app/dist/ && \
    echo "=== DIST CONTENT ===" && \
    ls -la /app/dist/content/ && \
    echo "=== DIST BACKGROUND ===" && \
    ls -la /app/dist/background/ || true

# Default command - just keep container running
CMD ["tail", "-f", "/dev/null"]