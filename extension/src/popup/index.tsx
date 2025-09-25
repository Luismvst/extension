/**
 * Popup entry point for the Chrome extension.
 */

import React from 'react'
import { createRoot } from 'react-dom/client'
import MainApp from './MainApp'

// Render the popup app
const container = document.getElementById('root')
if (container) {
  const root = createRoot(container)
  root.render(<MainApp />)
}