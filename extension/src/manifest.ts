import { defineManifest } from '@crxjs/vite-plugin'

export default defineManifest({
  name: 'Mirakl-TIPSA Orchestrator',
  description: 'Orchestrator for Mirakl marketplace orders to TIPSA carrier',
  version: '0.2.0',
  manifest_version: 3,
  icons: {
    16: 'icons/icon-16.png',
    32: 'icons/icon-32.png',
    48: 'icons/icon-48.png',
    128: 'icons/icon-128.png',
  },
  action: {
    default_popup: 'popup/index.html',
    default_title: 'Mirakl-TIPSA Orchestrator',
  },
  options_page: 'options/index.html',
  content_scripts: [
    {
      matches: ['*://*.tipsa.com/*'],
      js: ['content/index.js'],
      css: ['content/styles.css'],
    },
  ],
  background: {
    service_worker: 'background/index.js',
  },
  
  permissions: [
    'storage',
    'activeTab',
    'scripting',
  ],
  host_permissions: [
    '*://*.tipsa.com/*',
    '*://localhost:*/*',
    '*://127.0.0.1:*/*',
  ],
  web_accessible_resources: [
    {
      resources: ['content/*'],
      matches: ['*://*.tipsa.com/*'],
    },
  ],
})