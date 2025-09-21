import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock Chrome APIs
const mockChrome = {
  runtime: {
    onInstalled: {
      addListener: vi.fn()
    },
    onMessage: {
      addListener: vi.fn()
    },
    onStartup: {
      addListener: vi.fn()
    },
    onSuspend: {
      addListener: vi.fn()
    },
    getManifest: vi.fn(() => ({
      version: '0.2.0',
      name: 'Mirakl Tipsa MVP'
    })),
    openOptionsPage: vi.fn(),
    sendMessage: vi.fn()
  },
  tabs: {
    onUpdated: {
      addListener: vi.fn()
    },
    sendMessage: vi.fn(),
    query: vi.fn()
  },
  scripting: {
    executeScript: vi.fn()
  },
  action: {
    onClicked: {
      addListener: vi.fn()
    },
    openPopup: vi.fn()
  },
  contextMenus: {
    create: vi.fn(),
    onClicked: {
      addListener: vi.fn()
    }
  },
  storage: {
    local: {
      get: vi.fn(),
      set: vi.fn(),
      remove: vi.fn(),
      clear: vi.fn()
    }
  }
}

// Set up global Chrome mock
Object.defineProperty(global, 'chrome', {
  value: mockChrome,
  writable: true
})

// Mock BUILD_INFO
Object.defineProperty(global, 'BUILD_INFO', {
  value: {
    commit: 'test-commit',
    buildTime: '2024-01-01T00:00:00.000Z',
    buildNumber: '1234567890'
  },
  writable: true
})