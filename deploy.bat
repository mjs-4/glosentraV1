@echo off
echo 🚀 Building Glosentra static site...

REM Build the static site
npm run build

REM Copy router.js to dist
copy "static\js\router.js" "dist\static\js\" /Y

echo ✅ Static site built successfully!
echo 📁 Files are in the 'dist' directory
echo 🌐 To test locally, run: cd dist && python -m http.server 8000
echo 📤 Ready for GitHub Pages deployment!
pause
