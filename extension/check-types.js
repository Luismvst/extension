#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Verificando TypeScript...\n');

try {
  // Check if node_modules exists
  if (!fs.existsSync('node_modules')) {
    console.log('📦 Instalando dependencias...');
    execSync('npm install', { stdio: 'inherit' });
  }

  // Run TypeScript check
  console.log('🔧 Ejecutando verificación de tipos...');
  execSync('npx tsc --noEmit', { stdio: 'inherit' });
  
  console.log('✅ TypeScript check passed!');
} catch (error) {
  console.error('❌ TypeScript check failed:');
  console.error(error.message);
  process.exit(1);
}
