#!/usr/bin/env bash
# Render every Pithos diagram source in docs/diagrams/. Run from anywhere. Needs: d2 (https://d2lang.com) and python3 (to-scale plans/sections).
#   d2 install:  curl -fsSL https://d2lang.com/install.sh | sh -s --      (or a release binary from github.com/terrastruct/d2)
set -euo pipefail
cd "$(dirname "$0")/../docs/diagrams"
for f in d2-*.d2; do
  d2 --layout=dagre "$f" "${f%.d2}.svg"      # vector
  d2 --layout=dagre "$f" "${f%.d2}.png"      # raster (the PDF build embeds the PNG; d2 PNG export uses Playwright/Chromium)
done
python3 ../../tools/make_svgs.py             # to-scale floor plans + side section (single-layout-top*.svg, single-airflow.svg, cluster layout)
