#!/usr/bin/env bash
# PostgreSQL backup script for Vuvoz
# Usage: ./scripts/backup_db.sh [output_dir]
set -e
OUTPUT_DIR="${1:-./backups}"
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -n "$DATABASE_URL" ]; then
  pg_dump "$DATABASE_URL" > "$OUTPUT_DIR/vuvoz_$TIMESTAMP.sql"
  echo "Backup saved to $OUTPUT_DIR/vuvoz_$TIMESTAMP.sql"
else
  echo "DATABASE_URL not set. For SQLite, copy db.sqlite3 manually."
fi
