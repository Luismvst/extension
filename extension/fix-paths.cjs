const fs = require('fs');
const path = require('path');

// Get actual asset files
const assetsDir = path.join(__dirname, 'dist', 'assets');
const assetFiles = fs.existsSync(assetsDir) ? fs.readdirSync(assetsDir) : [];

// Create mapping of asset names to actual files
const assetMap = {};
assetFiles.forEach(file => {
  if (file.endsWith('.js')) {
    const baseName = file.split('-')[0];
    assetMap[baseName] = file;
  }
});

console.log('Found assets:', assetMap);

// Fix paths in HTML files
const htmlFiles = ['popup.html', 'options.html'];

htmlFiles.forEach(file => {
  const filePath = path.join(__dirname, 'dist', file);
  
  if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Replace ../../ with ./
    content = content.replace(/\.\.\/\.\.\//g, './');
    
    // Update asset file names to actual files
    Object.keys(assetMap).forEach(baseName => {
      const pattern = new RegExp(`assets/${baseName}-[A-Za-z0-9]+\\.js`, 'g');
      content = content.replace(pattern, `assets/${assetMap[baseName]}`);
    });
    
    fs.writeFileSync(filePath, content);
    console.log(`Fixed paths in ${file}`);
  }
});

console.log('Path fixing completed');
