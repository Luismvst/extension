# Mirakl Tipsa MVP - Chrome Extension

Chrome extension (MV3) for orchestrating Mirakl marketplace orders to TIPSA carrier with a modern React UI and comprehensive testing suite.

## 🚀 Features

- **3-Step Workflow**: Load Orders → Create Shipments → Upload Tracking
- **Modern UI**: Material-UI components with responsive design
- **Carrier Prediction**: Smart carrier selection based on order criteria
- **CSV Export**: Excel-compatible export with TIPSA headers
- **Frontend Logging**: Comprehensive action logging with CSV download
- **TypeScript**: Strict type checking and modern development experience
- **Testing**: Unit tests (Vitest) and E2E tests (Playwright)
- **Docker**: 100% containerized build and testing

## 🏗️ Architecture

### Frontend (Chrome Extension MV3)
- **Popup**: React app with Material-UI for main workflow
- **Background**: Service worker for API communication
- **Content Scripts**: TIPSA website integration
- **Options**: Configuration page for CSV settings

### Backend Integration
- **Mirakl API**: Order fetching and tracking upload
- **TIPSA API**: Shipment creation and label generation
- **Orchestrator**: Central coordination service

## 🛠️ Development

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Chrome browser

### Quick Start

```bash
# Build and test everything in Docker
docker-compose run --rm builder

# Run E2E tests
docker-compose run --rm e2e

# Package extension
docker-compose run --rm artifact
```

### Local Development

```bash
cd extension

# Install dependencies
npm install

# Development server
npm run dev

# Type checking
npm run typecheck

# Linting
npm run lint
npm run lint:fix

# Unit tests
npm run test:unit

# E2E tests
npm run test:e2e

# Build
npm run build

# Package
npm run package:zip
```

## 📦 Building & Testing

### Docker Build Process

1. **Dependencies**: Install with frozen lockfile
2. **Type Check**: Strict TypeScript validation
3. **Lint**: ESLint with Prettier formatting
4. **Unit Tests**: Vitest with 80% coverage threshold
5. **Build**: Vite multi-entry build
6. **E2E Tests**: Playwright browser automation
7. **Package**: ZIP with checksums

### Build Verification

The extension includes **SENTINELS** to verify correct loading:

- **BG SENTINEL**: Console log in service worker
- **POPUP SENTINEL**: Data attribute in popup DOM
- **Build Info**: Commit hash and timestamp display

### Loading Extension

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `extension/dist/` folder
5. Verify sentinels in console and UI

## 🧪 Testing

### Unit Tests
- **Background Script**: Message handling and API responses
- **FrontLogger**: Log management and CSV export
- **CsvExporter**: Data transformation and formatting
- **UI Components**: React component behavior

### E2E Tests
- **Extension Loading**: Verify sentinels and build info
- **Workflow**: Complete order processing flow
- **UI Interaction**: Button states and user feedback

### Coverage Requirements
- Lines: 80%
- Functions: 80%
- Branches: 80%
- Statements: 80%

## 📁 Project Structure

```
extension/
├── src/
│   ├── background/          # Service worker
│   ├── content/             # Content scripts
│   ├── popup/               # React popup app
│   ├── options/             # Options page
│   ├── lib/                 # Utilities (logger, CSV)
│   ├── types/               # TypeScript definitions
│   └── __tests__/           # Unit tests
├── tests/e2e/               # E2E tests
├── scripts/                 # Build scripts
├── dist/                    # Built extension
└── out/                     # Packaged artifacts
```

## 🔧 Configuration

### Environment Variables
- `BUILD_NUMBER`: Incremental build number
- `SHORT_SHA`: Git commit short hash
- `BUILD_TIME`: ISO timestamp

### Manifest Configuration
- **Version**: Auto-incremented with build number
- **Permissions**: Minimal required permissions
- **Content Scripts**: TIPSA website matching
- **Web Accessible Resources**: Proper resource exposure

## 📊 Monitoring & Logging

### Frontend Logging
- **Actions**: User interactions and API calls
- **Storage**: Chrome storage with 2000 entry limit
- **Export**: CSV download with timestamps
- **Rotation**: Automatic cleanup of old entries

### Build Verification
- **Sentinels**: Unique identifiers per build
- **Version Check**: Manifest version validation
- **Console Logs**: Service worker activity
- **UI Elements**: Build info display

## 🚀 Deployment

### Development
1. Build in Docker: `docker-compose run --rm builder`
2. Load in Chrome: `chrome://extensions/`
3. Verify sentinels in console
4. Test workflow end-to-end

### Production
1. Run full test suite
2. Package with checksums
3. Upload to Chrome Web Store
4. Monitor with logging

## 🐛 Troubleshooting

### Common Issues

**Extension not loading new version:**
- Check BG SENTINEL in service worker console
- Verify POPUP SENTINEL in DOM
- Reload extension in chrome://extensions/

**Build failures:**
- Run `npm run clean` before building
- Check TypeScript errors: `npm run typecheck`
- Verify linting: `npm run lint`

**Tests failing:**
- Check Chrome API mocks in setupTests.ts
- Verify test environment configuration
- Run tests individually for debugging

### Debug Commands

```bash
# Check build info
npm run build && cat dist/manifest.json | grep version

# Verify sentinels
npm run verify:sentinels

# Check coverage
npm run test:unit -- --coverage

# Debug E2E
npm run test:e2e:ui
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Run tests: `docker-compose run --rm builder`
4. Submit pull request

---

**Built with ❤️ using TypeScript, React, Material-UI, and Docker**