# Glosentra - GitHub Pages Deployment

This repository contains both a Flask web application and a static site optimized for GitHub Pages deployment.

## Static Site (GitHub Pages)

The static site is located in the root directory and includes:

- `index.html` - Main landing page
- `deploy_detect.html` - Object detection demo page
- `404.html` - Custom 404 error page
- `static/` - CSS, JavaScript, and other assets
- `static/js/router.js` - Client-side router for navigation

### Features

- **Client-side routing** - Navigate between pages without full page reloads
- **Responsive design** - Works on desktop and mobile devices
- **Modern UI** - Built with Tailwind CSS and custom styling
- **GitHub Pages ready** - Optimized for static hosting

### Deployment

1. **Automatic Deployment**: The site is automatically deployed to GitHub Pages when you push to the main branch via GitHub Actions.

2. **Manual Deployment**: 
   ```bash
   npm install
   npm run build
   # The dist/ folder contains the built static site
   ```

3. **Local Development**:
   ```bash
   npm run dev
   # Serves the site at http://localhost:8000
   ```

## Flask Application

The full Flask application is located in `apps/web/` and provides:

- Real-time computer vision inference
- Object detection, segmentation, classification, and pose estimation
- Analytics dashboard
- Document search with ChromaDB
- REST API endpoints

### Running the Flask App

```bash
# Install dependencies
pip install -r apps/web/requirements.txt

# Run the application
python apps/web/app.py
```

The Flask app will be available at `http://localhost:5000`.

## Project Structure

```
├── index.html                 # Static site homepage
├── deploy_detect.html         # Object detection demo
├── 404.html                  # Custom 404 page
├── static/                   # Static assets
│   ├── css/theme.css         # Custom CSS
│   └── js/router.js          # Client-side router
├── apps/web/                 # Flask application
│   ├── app.py               # Flask app entry point
│   ├── glosentra/           # Main application package
│   └── requirements.txt     # Python dependencies
├── .github/workflows/        # GitHub Actions
│   └── deploy.yml           # Deployment workflow
└── package.json             # Node.js dependencies
```

## GitHub Pages Configuration

The site is configured to work with GitHub Pages:

1. **Repository Settings**: Enable GitHub Pages in repository settings
2. **Source**: Deploy from GitHub Actions
3. **Custom Domain**: Optional - add your domain in the workflow file

## Development

### Static Site Development

```bash
# Install dependencies
npm install

# Build the site
npm run build

# Serve locally
npm run serve
```

### Flask App Development

```bash
# Install Python dependencies
pip install -r apps/web/requirements.txt

# Run in development mode
python apps/web/app.py
```

## Features

### Static Site
- ✅ Responsive design
- ✅ Client-side routing
- ✅ Modern UI with Tailwind CSS
- ✅ GitHub Pages deployment
- ✅ Custom 404 page
- ✅ SEO optimized

### Flask Application
- ✅ Real-time computer vision
- ✅ Multiple AI models (YOLO v11)
- ✅ REST API
- ✅ Analytics dashboard
- ✅ Document search
- ✅ File upload handling

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
