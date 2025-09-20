const fs = require('fs');
const path = require('path');

// Create a simple SVG icon
const createIcon = (size) => {
  return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
    <rect width="${size}" height="${size}" fill="#1976d2" rx="4"/>
    <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" 
          font-family="Arial, sans-serif" font-size="${size * 0.4}" fill="white" font-weight="bold">
      M-T
    </text>
  </svg>`;
};

// Create icons directory
const iconsDir = path.join(__dirname, 'dist', 'icons');
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

// Create different sized icons
const sizes = [16, 32, 48, 128];
sizes.forEach(size => {
  const svg = createIcon(size);
  const filename = `icon-${size}.png`;
  
  // For now, we'll create a simple text file that represents the icon
  // In a real scenario, you'd convert SVG to PNG
  const iconContent = `# Icon ${size}x${size} - Mirakl-TIPSA Orchestrator
# This is a placeholder icon file
# In production, replace with actual PNG files
${svg}`;
  
  fs.writeFileSync(path.join(iconsDir, filename), iconContent);
  console.log(`Created ${filename}`);
});

console.log('Icons created successfully!');
