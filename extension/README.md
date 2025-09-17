# Mirakl CSV Extension

Chrome extension (MV3) that intercepts CSV exports from Mirakl marketplaces and generates TIPSA-compatible files.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Chrome/Chromium browser
- pnpm (recommended) or npm

### Installation

1. **Clone and install dependencies**
```bash
git clone https://github.com/Luismvst/extension.git
cd extension/extension
pnpm install
```

2. **Build the extension**
```bash
pnpm build
```

3. **Load in Chrome**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension/dist` folder

### Development

```bash
# Start development server
pnpm dev

# Run tests
pnpm test

# Run E2E tests
pnpm test:e2e

# Build for production
pnpm build

# Lint code
pnpm lint

# Type check
pnpm type-check
```

## 📁 Project Structure

```
src/
├── background/          # Service worker
├── content/            # Content scripts
├── popup/              # Extension popup UI
├── options/            # Extension options page
├── common/             # Shared types and utilities
├── lib/                # Core libraries
├── mappers/            # CSV mappers (TIPSA, OnTime)
└── styles/             # Global styles
```

## 🔧 Configuration

The extension can be configured through the options page:

- **Auto Export**: Automatically export CSV when detected
- **Default Service**: Default TIPSA service type
- **Cleanup Days**: Days to keep orders in storage
- **Notifications**: Show success/error notifications
- **Debug Mode**: Enable detailed logging

## 🧪 Testing

### Unit Tests
```bash
pnpm test
```

### E2E Tests
```bash
# Start test portal
pnpm dev:portal

# Run E2E tests
pnpm test:e2e
```

### Test Portal
The project includes a test portal at `http://localhost:3000` that simulates Mirakl marketplaces for testing.

## 📦 Building

### Development Build
```bash
pnpm build
```

### Production Build
```bash
NODE_ENV=production pnpm build
```

## 🔍 Debugging

1. **Extension Console**: Right-click extension icon → "Inspect popup"
2. **Background Script**: Go to `chrome://extensions/` → Click "Inspect views: background page"
3. **Content Script**: Open DevTools on any Mirakl page
4. **Debug Mode**: Enable in extension options for detailed logging

## 🚨 Troubleshooting

### Common Issues

**Extension not loading**
- Check that all files are in the `dist` folder
- Verify manifest.json is valid
- Check Chrome console for errors

**CSV not intercepting**
- Ensure you're on a supported Mirakl marketplace
- Check content script is loaded (DevTools → Console)
- Verify export button has correct selectors

**Popup not showing orders**
- Check background script for errors
- Verify storage permissions
- Check network requests in DevTools

### Debug Steps

1. Enable debug mode in extension options
2. Check browser console for errors
3. Verify extension permissions
4. Test with the provided test portal

## 📋 Supported Marketplaces

- **Carrefour** (carrefour.fr)
- **Leroy Merlin** (leroymerlin.fr)
- **Adeo** (adeo.com, adeo-group.com)

## 🔄 Data Flow

1. **Interception**: Content script detects CSV export clicks
2. **Fetch**: Downloads CSV data with authentication
3. **Parse**: Converts CSV to standardized order format
4. **Validate**: Validates data with Zod schemas
5. **Store**: Saves orders to Chrome storage
6. **Display**: Shows orders in popup interface
7. **Export**: Generates TIPSA-compatible CSV

## 🛡️ Security

- **PII Protection**: Sensitive data is obfuscated in storage
- **Local Storage**: All data stored locally, no external transmission
- **Permissions**: Minimal required permissions
- **Validation**: All data validated before processing

## 📈 Performance

- **Lazy Loading**: Components loaded on demand
- **Efficient Storage**: Data compressed and cleaned regularly
- **Background Processing**: Heavy operations in service worker
- **Memory Management**: Automatic cleanup of old data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

## 🔗 Links

- [Main Documentation](../docs/README.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)
- [MVP Plan](../docs/MVP_PLAN.md)
- [Changelog](../CHANGELOG.md)
