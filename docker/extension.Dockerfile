# Use Node 18 Alpine image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY extension/package.json extension/pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY extension/ .

# Build the extension
RUN pnpm build

# Create artifacts directory
RUN mkdir -p /artifacts/dist

# Copy built extension to artifacts
RUN cp -r dist/* /artifacts/dist/

# Expose artifacts volume
VOLUME ["/artifacts"]

# Default command (just exit, as this is a build-only container)
CMD ["echo", "Extension build completed. Check /artifacts/dist for the built extension."]
