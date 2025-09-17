import { defineManifest } from '@crxjs/vite-plugin'

export default defineManifest({
  manifest_version: 3,
  name: 'Mirakl CSV Extension',
  version: '0.1.0',
  description: 'Intercept Mirakl CSV exports and generate TIPSA-compatible files',
  permissions: [
    'storage',
    'activeTab',
    'scripting'
  ],
  host_permissions: [
    'https://*.mirakl.net/*',
    'https://*.carrefour.fr/*',
    'https://*.leroymerlin.fr/*',
    'https://*.adeo.com/*',
    'https://*.adeo-group.com/*',
    'http://localhost:*/*'
  ],
  background: {
    service_worker: 'background.js',
    type: 'module'
  },
  content_scripts: [
    {
      matches: [
        'https://*.mirakl.net/*',
        'https://*.carrefour.fr/*',
        'https://*.leroymerlin.fr/*',
        'https://*.adeo.com/*',
        'https://*.adeo-group.com/*',
        'http://localhost:*/*'
      ],
      js: ['content.js'],
      run_at: 'document_end'
    }
  ],
  action: {
    default_popup: 'popup.html',
    default_title: 'Mirakl CSV Extension',
    default_icon: {
      16: 'icons/icon-16.png',
      32: 'icons/icon-32.png',
      48: 'icons/icon-48.png',
      128: 'icons/icon-128.png'
    }
  },
  icons: {
    16: 'icons/icon-16.png',
    32: 'icons/icon-32.png',
    48: 'icons/icon-48.png',
    128: 'icons/icon-128.png'
  },
  web_accessible_resources: [
    {
      resources: ['popup.html', 'options.html'],
      matches: ['<all_urls>']
    }
  ]
})
