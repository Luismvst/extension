import '@testing-library/jest-dom'

// Mock chrome APIs
const mockChrome = {
  runtime: {
    sendMessage: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
      removeListener: jest.fn(),
    },
    onInstalled: {
      addListener: jest.fn(),
    },
    onStartup: {
      addListener: jest.fn(),
    },
    onSuspend: {
      addListener: jest.fn(),
    },
  },
  storage: {
    local: {
      get: jest.fn(),
      set: jest.fn(),
      remove: jest.fn(),
      clear: jest.fn(),
      getBytesInUse: jest.fn(),
      QUOTA_BYTES: 5242880,
    },
  },
  tabs: {
    sendMessage: jest.fn(),
  },
  alarms: {
    create: jest.fn(),
    onAlarm: {
      addListener: jest.fn(),
    },
  },
}

Object.assign(global, { chrome: mockChrome })

// Mock fetch
global.fetch = jest.fn()

// Mock URL.createObjectURL and URL.revokeObjectURL
Object.defineProperty(URL, 'createObjectURL', {
  writable: true,
  value: jest.fn(() => 'mock-url'),
})

Object.defineProperty(URL, 'revokeObjectURL', {
  writable: true,
  value: jest.fn(),
})

// Mock document.createElement for download functionality
const mockClick = jest.fn()
const mockAppendChild = jest.fn()
const mockRemoveChild = jest.fn()

Object.defineProperty(document, 'createElement', {
  writable: true,
  value: jest.fn((tagName: string) => {
    if (tagName === 'a') {
      return {
        href: '',
        download: '',
        style: { visibility: '' },
        click: mockClick,
        setAttribute: jest.fn(),
      }
    }
    return {}
  }),
})

Object.defineProperty(document.body, 'appendChild', {
  writable: true,
  value: mockAppendChild,
})

Object.defineProperty(document.body, 'removeChild', {
  writable: true,
  value: mockRemoveChild,
})
