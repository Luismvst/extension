/**
 * Build information for tracing and debugging.
 * This file is generated at build time to ensure fresh builds.
 */

export const BUILD_INFO = {
  buildTime: new Date().toISOString(),
  // si hay var de entorno, añade commit corto
  commit: 'dev',
  version: '0.2.0',
  sentinel: 'SENTINEL:NEW-POPUP-UI'
} as const;

export const getBuildInfo = () => BUILD_INFO;
