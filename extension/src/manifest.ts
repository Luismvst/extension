import { defineManifest } from '@crxjs/vite-plugin'

const EXT_VERSION = process.env.EXT_VERSION || Date.now().toString()
const VERSION = `0.2.${EXT_VERSION}`

export default defineManifest({
  name: 'Mirakl Tipsa MVP',
  description: 'Chrome extension for orchestrating Mirakl marketplace orders to TIPSA carrier - MVP Version',
  version: VERSION,
  manifest_version: 3,
  icons: {
    16: 'icons/icon-16.png',
    32: 'icons/icon-32.png',
    48: 'icons/icon-48.png',
    128: 'icons/icon-128.png',
  },
  action: {
    default_popup: 'popup/index.html',
    default_title: 'Mirakl Tipsa MVP',
  },
  options_page: 'options/index.html',
  content_scripts: [
    {
      matches: ['*://*.tipsa.com/*', '*://*.tip-sa.com/*'],
      js: ['content/index.js'],
      css: ['content/styles.css'],
    },
  ],
  background: {
    service_worker: 'background.js',
    type: 'module'
  },
  
  permissions: [
    'storage',
    'activeTab',
    'scripting',
    'tabs',
    'contextMenus'
  ],
  host_permissions: [
    '*://*.tipsa.com/*',
    '*://*.tip-sa.com/*',
    'http://localhost:8080/*',
    'http://backend:8080/*',
  ],
  web_accessible_resources: [
    {
      resources: ['content/*', 'assets/*', '*.css'],
      matches: ['<all_urls>'],
    },
  ],
})