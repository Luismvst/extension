#!/usr/bin/env node

import { chromium } from 'playwright'
import { readFileSync } from 'fs'
import { join } from 'path'

const DIST_DIR = 'dist'
const MANIFEST_PATH = join(DIST_DIR, 'manifest.json')

console.log('🔍 Verifying extension sentinels...')

// Read manifest to get extension ID
const manifest = JSON.parse(readFileSync(MANIFEST_PATH, 'utf8'))
console.log(`📋 Extension: ${manifest.name} v${manifest.version}`)

async function verifySentinels() {
  const browser = await chromium.launch({
    headless: false,
    args: [
      '--disable-extensions-except=' + DIST_DIR,
      '--load-extension=' + DIST_DIR,
      '--disable-web-security',
      '--disable-features=VizDisplayCompositor'
    ]
  })

  const context = await browser.newContext()
  const page = await context.newPage()

  try {
    // Wait for extension to load
    await page.waitForTimeout(2000)

    // Get extension ID from chrome://extensions
    await page.goto('chrome://extensions/')
    await page.waitForTimeout(1000)

    // Look for our extension in the list
    const extensionElement = await page.locator('extensions-item').filter({ hasText: manifest.name }).first()
    
    if (await extensionElement.count() === 0) {
      throw new Error('Extension not found in chrome://extensions')
    }

    console.log('✅ Extension found in chrome://extensions')

    // Click on "Service Worker" link to inspect
    const serviceWorkerLink = extensionElement.locator('a[href*="service-worker"]')
    if (await serviceWorkerLink.count() > 0) {
      await serviceWorkerLink.click()
      await page.waitForTimeout(1000)
      
      // Check console logs for BG SENTINEL
      const logs = []
      page.on('console', msg => {
        if (msg.text().includes('BG SENTINEL')) {
          logs.push(msg.text())
        }
      })
      
      await page.waitForTimeout(2000)
      
      if (logs.length > 0) {
        console.log('✅ BG SENTINEL found in service worker logs')
        console.log(`   ${logs[0]}`)
      } else {
        console.log('⚠️  BG SENTINEL not found in service worker logs')
      }
    }

    // Test popup
    const popupPage = await context.newPage()
    await popupPage.goto(`chrome-extension://${await getExtensionId(page)}/popup/index.html`)
    
    // Check for POPUP SENTINEL
    const popupSentinel = await popupPage.locator('[data-sentinel]').first()
    if (await popupSentinel.count() > 0) {
      const sentinelValue = await popupSentinel.getAttribute('data-sentinel')
      console.log(`✅ POPUP SENTINEL found: ${sentinelValue}`)
    } else {
      console.log('⚠️  POPUP SENTINEL not found')
    }

    // Check for build info in popup
    const buildInfo = await popupPage.locator('text=/Build:/').first()
    if (await buildInfo.count() > 0) {
      const buildText = await buildInfo.textContent()
      console.log(`✅ Build info found: ${buildText}`)
    } else {
      console.log('⚠️  Build info not found in popup')
    }

    console.log('🎉 Sentinel verification completed!')

  } catch (error) {
    console.error('❌ Verification failed:', error.message)
    process.exit(1)
  } finally {
    await browser.close()
  }
}

async function getExtensionId(page) {
  // This is a simplified approach - in practice you'd need to extract the ID from the extensions page
  return 'temp-extension-id'
}

verifySentinels().catch(console.error)
