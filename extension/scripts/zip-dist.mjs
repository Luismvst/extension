#!/usr/bin/env node

import { createWriteStream } from 'fs'
import { createReadStream } from 'fs'
import { readFileSync, readdirSync, statSync } from 'fs'
import { join, relative } from 'path'
import { createHash } from 'crypto'
import archiver from 'archiver'
import { execSync } from 'child_process'

const BUILD_NUMBER = process.env.BUILD_NUMBER || Date.now()
const SHORT_SHA = process.env.SHORT_SHA || execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim()
const VERSION = JSON.parse(readFileSync('package.json', 'utf8')).version

const ZIP_NAME = `extension-${VERSION}-${SHORT_SHA}.zip`
const OUT_DIR = 'out'
const DIST_DIR = 'dist'

// Ensure output directory exists
import { mkdirSync } from 'fs'
try {
  mkdirSync(OUT_DIR, { recursive: true })
} catch (e) {
  // Directory already exists
}

console.log(`📦 Creating ${ZIP_NAME} from ${DIST_DIR}/`)

const output = createWriteStream(join(OUT_DIR, ZIP_NAME))
const archive = archiver('zip', { zlib: { level: 9 } })

output.on('close', () => {
  console.log(`✅ Created ${ZIP_NAME} (${archive.pointer()} bytes)`)
  
  // Generate checksum
  const fileBuffer = readFileSync(join(OUT_DIR, ZIP_NAME))
  const hashSum = createHash('sha256')
  hashSum.update(fileBuffer)
  const hex = hashSum.digest('hex')
  
  const checksumFile = join(OUT_DIR, 'SHA256SUMS')
  const checksumContent = `${hex}  ${ZIP_NAME}\n`
  
  try {
    readFileSync(checksumFile, 'utf8')
    // Append to existing file
    const fs = await import('fs')
    fs.appendFileSync(checksumFile, checksumContent)
  } catch {
    // Create new file
    createWriteStream(checksumFile).write(checksumContent)
  }
  
  console.log(`📋 Checksum: ${hex}`)
  console.log(`📁 Output: ${OUT_DIR}/${ZIP_NAME}`)
})

archive.on('error', (err) => {
  console.error('❌ Archive error:', err)
  process.exit(1)
})

archive.pipe(output)

// Add all files from dist directory
function addDirectoryToArchive(dir, baseDir = '') {
  const items = readdirSync(dir)
  
  for (const item of items) {
    const fullPath = join(dir, item)
    const stat = statSync(fullPath)
    const relativePath = join(baseDir, item)
    
    if (stat.isDirectory()) {
      addDirectoryToArchive(fullPath, relativePath)
    } else {
      archive.append(createReadStream(fullPath), { name: relativePath })
    }
  }
}

addDirectoryToArchive(DIST_DIR)

archive.finalize()
