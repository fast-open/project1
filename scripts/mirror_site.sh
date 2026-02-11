#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TMP_SITEMAP="$(mktemp)"
trap 'rm -f "$TMP_SITEMAP"' EXIT

curl -L --max-time 60 http://www.dasoftn.in/wp-sitemap-posts-page-1.xml -o "$TMP_SITEMAP"
python - <<'PY' "$TMP_SITEMAP" "$ROOT_DIR/scripts/urls.txt"
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sitemap_path, out_path = sys.argv[1], sys.argv[2]
xml = Path(sitemap_path).read_text(encoding='utf-8')
root = ET.fromstring(xml)
ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls = [loc.text.strip() for loc in root.findall('sm:url/sm:loc', ns)]
Path(out_path).write_text('\n'.join(urls) + '\n', encoding='utf-8')
print(f"Collected {len(urls)} URLs")
PY

rm -rf "$ROOT_DIR/cloned-site"
mkdir -p "$ROOT_DIR/cloned-site"

wget \
  --page-requisites \
  --convert-links \
  --adjust-extension \
  --span-hosts \
  --domains=www.dasoftn.in,dasoftn.in \
  --no-parent \
  --directory-prefix="$ROOT_DIR/cloned-site" \
  --input-file="$ROOT_DIR/scripts/urls.txt" \
  --execute robots=off \
  --no-verbose

# Keep repository PR-friendly for platforms that reject binary files.
# This retains HTML/CSS/JS/SVG text assets and removes binary assets.
python - <<'PY' "$ROOT_DIR/cloned-site"
from pathlib import Path
root = Path(__import__('sys').argv[1])
BINARY_SUFFIXES = {
    '.woff', '.woff2', '.ttf', '.eot', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico', '.pdf'
}
removed = 0
for p in root.rglob('*'):
    if not p.is_file():
        continue
    name = p.name.lower()
    if any(ext in name for ext in BINARY_SUFFIXES) or name.endswith('.eot?'):
        p.unlink()
        removed += 1
print(f"Removed {removed} binary files")
PY
