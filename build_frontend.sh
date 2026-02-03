#!/usr/bin/env bash
# Build Vue app and output to frontend/dist (Django will serve from here + collectstatic)
set -e
cd "$(dirname "$0")/frontend"
npm ci --omit=optional
npm run build
echo "Frontend built to frontend/dist"
