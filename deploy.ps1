# PowerShell deployment script for Glosentra static site

Write-Host "🚀 Building Glosentra static site..." -ForegroundColor Green

# Build the static site
npm run build

# Copy router.js to dist
Copy-Item "static/js/router.js" "dist/static/js/" -Force

Write-Host "✅ Static site built successfully!" -ForegroundColor Green
Write-Host "📁 Files are in the 'dist' directory" -ForegroundColor Blue
Write-Host "🌐 To test locally, run: cd dist && python -m http.server 8000" -ForegroundColor Yellow
Write-Host "📤 Ready for GitHub Pages deployment!" -ForegroundColor Cyan
