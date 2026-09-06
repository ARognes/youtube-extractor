#!/usr/bin/env bash
set -e

echo "🚀 Building SvelteKit Visualizer for GitHub Pages..."
cd "$(dirname "$0")/../visualizer"

export BASE_PATH="/youtube-extractor"
# Prefer modern node if in nvm
if [ -d "$HOME/.nvm/versions/node/v22.13.0/bin" ]; then
    export PATH="$HOME/.nvm/versions/node/v22.13.0/bin:$PATH"
fi

npm run build

echo "📦 Preparing gh-pages deployment..."
TMP_DIR=$(mktemp -d)
cp -r build/* "$TMP_DIR/"
touch "$TMP_DIR/.nojekyll"

cd ..
git checkout gh-pages
# Clean existing static files
rm -rf _app index.html 404.html robots.txt tag_hierarchy_manifest.json .nojekyll
cp -r "$TMP_DIR"/* .
rm -rf "$TMP_DIR"

git add index.html 404.html robots.txt tag_hierarchy_manifest.json .nojekyll _app/
if git diff --staged --quiet; then
    echo "✨ No visual changes detected on gh-pages."
else
    git commit -m "deploy: update static SvelteKit visualizer build for GitHub Pages"
    git push origin gh-pages
    echo "🎉 Successfully pushed update to gh-pages branch!"
fi

git checkout main
echo "Switched back to main branch."
