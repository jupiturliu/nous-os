#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf _site
mkdir -p _site/docs _site/demo _site/examples/runtime/research-records

cp index.html _site/
cp about.html _site/
cp research.html _site/
cp favicon.svg _site/
cp CNAME _site/
cp .nojekyll _site/
cp README.md _site/
cp ARCHITECTURE.md _site/
cp docs/*.md _site/docs/
cp -R docs/harness _site/docs/
cp demo/heartbeat-dashboard.html _site/demo/
cp demo/student-sandbox-v1.html _site/demo/
cp demo/student-sandbox-v1-guide.html _site/demo/
cp -R demo/assets _site/demo/
cp examples/runtime/dashboard-data.json _site/examples/runtime/
cp examples/runtime/research-records/latest.json _site/examples/runtime/research-records/

echo "Staged static site in $ROOT/_site"
