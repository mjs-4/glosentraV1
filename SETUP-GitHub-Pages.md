# GitHub Pages Setup Guide for Glosentra

This guide will help you deploy the Glosentra static site to GitHub Pages.

## Prerequisites

- GitHub account
- Git installed on your local machine
- Node.js installed (optional, for local development)

## Step 1: Prepare Your Repository

1. **Fork or Clone** this repository to your GitHub account
2. **Enable GitHub Pages** in your repository settings:
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` (will be created automatically by GitHub Actions)

## Step 2: Configure GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that will automatically deploy your site when you push to the main branch.

### Required Repository Settings

1. Go to your repository Settings
2. Navigate to Actions → General
3. Ensure "Allow all actions and reusable workflows" is selected
4. Save the settings

## Step 3: Deploy Your Site

### Automatic Deployment (Recommended)

1. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin main
   ```

2. **Check deployment status**:
   - Go to Actions tab in your repository
   - Look for "Deploy to GitHub Pages" workflow
   - Wait for it to complete successfully

3. **Access your site**:
   - Your site will be available at: `https://yourusername.github.io/your-repo-name`
   - GitHub will show the URL in the Pages settings

### Manual Deployment

If you prefer to deploy manually:

1. **Build the site**:
   ```bash
   # Windows
   deploy.bat
   
   # Or manually
   npm run build
   copy "static\js\router.js" "dist\static\js\" /Y
   ```

2. **Upload to GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / `master`
   - Folder: `/ (root)`
   - Save

## Step 4: Custom Domain (Optional)

If you have a custom domain:

1. **Add CNAME file**:
   ```bash
   echo "yourdomain.com" > CNAME
   git add CNAME
   git commit -m "Add custom domain"
   git push
   ```

2. **Update GitHub Actions workflow**:
   - Edit `.github/workflows/deploy.yml`
   - Uncomment and set the `cname` parameter:
     ```yaml
     with:
       github_token: ${{ secrets.GITHUB_TOKEN }}
       publish_dir: ./dist
       cname: yourdomain.com
     ```

## Step 5: Verify Deployment

1. **Check your site** at the GitHub Pages URL
2. **Test navigation** between pages
3. **Verify responsive design** on mobile devices
4. **Check 404 page** by visiting a non-existent URL

## Local Development

To test the site locally before deploying:

```bash
# Install dependencies (if you have Node.js)
npm install

# Build the site
npm run build

# Serve locally
cd dist
python -m http.server 8000
```

Visit `http://localhost:8000` to see your site.

## Troubleshooting

### Common Issues

1. **Site not updating**:
   - Check GitHub Actions workflow status
   - Ensure you're pushing to the correct branch
   - Wait a few minutes for GitHub Pages to update

2. **404 errors**:
   - Verify the `404.html` file is in the root directory
   - Check that all HTML files are properly linked

3. **CSS not loading**:
   - Ensure the `static/` directory is copied to `dist/`
   - Check file paths in HTML files

4. **Navigation not working**:
   - Verify `router.js` is in `dist/static/js/`
   - Check browser console for JavaScript errors

### Getting Help

- Check the GitHub Actions logs for deployment errors
- Verify all files are present in the `dist/` directory
- Test the site locally before deploying

## Features

Your deployed site includes:

- ✅ **Responsive Design** - Works on all devices
- ✅ **Client-side Routing** - Smooth navigation between pages
- ✅ **Modern UI** - Built with Tailwind CSS
- ✅ **Custom 404 Page** - Professional error handling
- ✅ **SEO Optimized** - Proper meta tags and structure
- ✅ **Fast Loading** - Optimized for performance

## Next Steps

1. **Customize Content** - Edit the HTML files to match your needs
2. **Add More Pages** - Create additional pages and update the router
3. **Integrate Backend** - Connect to your Flask API when needed
4. **Monitor Performance** - Use GitHub Pages analytics

## Support

For issues with this setup:
1. Check the troubleshooting section above
2. Review GitHub Actions logs
3. Open an issue in this repository

Happy deploying! 🚀
