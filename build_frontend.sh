#!/usr/bin/env bash
# Build Vue app and output to frontend/dist (Django will serve from here + collectstatic)
# Requires Node.js 18+ (Vite 5 uses top-level await)
set -e
REQUIRED_MAJOR=18
NODE_VER=$(node -v 2>/dev/null | sed -n 's/^v\([0-9]*\).*/\1/p')
if [ -z "$NODE_VER" ] || [ "$NODE_VER" -lt "$REQUIRED_MAJOR" ]; then
  echo "Error: Node.js $REQUIRED_MAJOR+ required. Current: $(node -v 2>/dev/null || echo 'not found')"
  echo "On Ubuntu, install with: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
  exit 1
fi
cd "$(dirname "$0")/frontend"

# Sync hero logo into bundled assets (committed in git; optional refresh from media/)
HERO_SRC="../media/products/Green Modern Ecological Solutions Earth Company Logo.png"
HERO_DST_ASSETS="src/assets/brand/zeleniy-schet-hero-logo.png"
HERO_DST_PUBLIC="public/zeleniy-schet-hero-logo.png"
mkdir -p src/assets/brand
if [ -f "$HERO_SRC" ]; then
  cp "$HERO_SRC" "$HERO_DST_ASSETS"
  cp "$HERO_SRC" "$HERO_DST_PUBLIC"
  echo "Copied hero logo to $HERO_DST_ASSETS"
elif [ ! -f "$HERO_DST_ASSETS" ]; then
  echo "Warning: hero logo missing at $HERO_DST_ASSETS (add file or place source in media/products/)"
fi

# On Linux, npm ci can miss @rollup/rollup-linux-x64-gnu when lockfile was created on Windows (npm bug #4828).
# Workaround: clean install so npm resolves optional deps for current platform.
if [ "$(uname -s)" = "Linux" ]; then
  rm -rf node_modules package-lock.json
  npm install
else
  npm ci --omit=optional
fi

npm run build
echo "Frontend built to frontend/dist"
