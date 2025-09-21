/**
 * Content script for TIPSA website integration.
 * 
 * This script detects when the user is on a TIPSA website and injects
 * the orchestrator overlay with buttons to load orders and create shipments.
 */

// CONTENT SENTINEL for build verification
declare const BUILD_INFO: { commit: string; buildTime: string; buildNumber: string }
console.log('CONTENT SENTINEL', BUILD_INFO.commit)

import { createRoot } from 'react-dom/client'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import OrchestratorOverlay from './OrchestratorOverlay'

// Check if we're on a TIPSA website
const isTipsaWebsite = (): boolean => {
  const hostname = window.location.hostname
  return hostname.includes('tip-sa.com') || hostname.includes('tipsa')
}

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2'
    },
    secondary: {
      main: '#dc004e'
    }
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif'
  }
})

// Initialize the content script
const initContentScript = (): void => {
  if (!isTipsaWebsite()) {
    console.log('Not on TIPSA website, skipping orchestrator overlay')
    return
  }

  console.log('TIPSA website detected, initializing orchestrator overlay')

  // Wait for the page to be fully loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectOverlay)
  } else {
    injectOverlay()
  }
}

const injectOverlay = (): void => {
  // Check if overlay already exists
  if (document.getElementById('mirakl-tipsa-orchestrator')) {
    return
  }

  // Create overlay container
  const overlayContainer = document.createElement('div')
  overlayContainer.id = 'mirakl-tipsa-orchestrator'
  overlayContainer.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    max-width: 400px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
  `

  // Add to page
  document.body.appendChild(overlayContainer)

  // Render React component
  const root = createRoot(overlayContainer)
  root.render(
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <OrchestratorOverlay />
    </ThemeProvider>
  )

  console.log('Orchestrator overlay injected successfully')
}

// Listen for messages from the extension
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Content script received message:', message)

  switch (message.type) {
    case 'INJECT_OVERLAY':
      injectOverlay()
      sendResponse({ success: true })
      break

    case 'REMOVE_OVERLAY':
      const overlay = document.getElementById('mirakl-tipsa-orchestrator')
      if (overlay) {
        overlay.remove()
        sendResponse({ success: true })
      } else {
        sendResponse({ success: false, error: 'Overlay not found' })
      }
      break

    case 'GET_PAGE_INFO':
      sendResponse({
        success: true,
        data: {
          url: window.location.href,
          title: document.title,
          hostname: window.location.hostname,
          isTipsaWebsite: isTipsaWebsite()
        }
      })
      break

    default:
      sendResponse({ success: false, error: 'Unknown message type' })
  }

  return true // Keep message channel open for async response
})

// Initialize when script loads
initContentScript()