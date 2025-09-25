/**
 * Main Application Component
 * 
 * This component wraps the entire application with the Material-UI theme
 * and provides the main layout structure.
 */

import React from 'react'
import { ThemeProvider } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'
import { theme } from '@/theme'
import PopupApp from './PopupApp'

const MainApp: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <PopupApp />
    </ThemeProvider>
  )
}

export default MainApp
