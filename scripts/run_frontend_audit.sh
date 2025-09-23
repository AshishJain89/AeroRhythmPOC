#!/usr/bin/env bash
set -euo pipefail

# Safer frontend audit script for Git-Bash / MINGW64
# Usage:
#   ./scripts/run_frontend_audit.sh ./frontend

# Resolve script dir and then project dir (absolute)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARG_DIR="${1:-.}"

# resolve to absolute path (work cross-platform)
if cd "$ARG_DIR" 2>/dev/null; then
  PROJECT_DIR="$(pwd -P)"
else
  echo "ERROR: cannot cd to provided path: $ARG_DIR" >&2
  exit 1
fi

# Make absolute paths for outputs
ROOT_DIR="$PROJECT_DIR"
OUTROOT="$ROOT_DIR/audit-output"
TIMESTAMP="$(date +%Y%m%d_%H%M%S 2>/dev/null || date +%Y%m%d_%H%M%S)"
OUTDIR="$OUTROOT/$TIMESTAMP"

# Create outbound directories (fail loudly if creation fails)
mkdir -p "$OUTDIR" || { echo "ERROR: mkdir -p $OUTDIR failed" >&2; exit 1; }

# Small function for safe writes (ensures parent exists)
safe_write() {
  local file="$1"; shift
  mkdir -p "$(dirname "$file")"
  printf "%s\n" "$@" > "$file"
}

safe_append() {
  local file="$1"; shift
  mkdir -p "$(dirname "$file")"
  printf "%s\n" "$@" >> "$file"
}

# Diagnostic header
safe_write "$OUTDIR/summary.txt" "Audit started: $(date)" "Project dir: $PROJECT_DIR" "OUTDIR: $OUTDIR"

# Search explicitly for package.json near project dir (maxdepth 3)
FOUND_PKG_JSON="$(find "$PROJECT_DIR" -maxdepth 3 -type f -name package.json 2>/dev/null | head -n1 || true)"
if [ -z "$FOUND_PKG_JSON" ]; then
  safe_append "$OUTDIR/summary.txt" "ERROR: No package.json found under $PROJECT_DIR"
  echo "ERROR: No package.json found under $PROJECT_DIR" >&2
  exit 1
fi

FRONTEND_DIR="$(dirname "$FOUND_PKG_JSON")"
safe_append "$OUTDIR/summary.txt" "Found package.json at: $FOUND_PKG_JSON"
cd "$FRONTEND_DIR"

# Record environment
safe_append "$OUTDIR/summary.txt" "Using FRONTEND_DIR: $(pwd -P)" "Node: $(node -v 2>/dev/null || echo 'node not found')" "NPM: $(npm -v 2>/dev/null || echo 'npm not found')"

# Install dependencies (lockfile-aware)
if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then
  safe_append "$OUTDIR/summary.txt" "Lockfile present: running npm ci..."
  npm ci 2>&1 | tee "$OUTDIR/npm_install.log" || true
else
  safe_append "$OUTDIR/summary.txt" "No lockfile: running npm install..."
  npm install 2>&1 | tee "$OUTDIR/npm_install.log" || true
fi

# Create placeholders
: > "$OUTDIR/eslint.log"
: > "$OUTDIR/tsc.log"
: > "$OUTDIR/test.log"
: > "$OUTDIR/build.log"
: > "$OUTDIR/code-warnings.txt"
: > "$OUTDIR/secrets.txt"
: > "$OUTDIR/npm_audit.json"
: > "$OUTDIR/npm_outdated.json"

# Run lint if possible
if grep -q '"eslint"' package.json 2>/dev/null || command -v npx >/dev/null 2>&1; then
  npx eslint "src/**/*.{js,jsx,ts,tsx}" --max-warnings=0 2>&1 | tee -a "$OUTDIR/eslint.log" || true
else
  safe_append "$OUTDIR/eslint.log" "ESLint not found or not configured"
fi

# TypeScript check if present
if [ -f tsconfig.json ]; then
  npx tsc --noEmit 2>&1 | tee -a "$OUTDIR/tsc.log" || true
else
  safe_append "$OUTDIR/tsc.log" "No tsconfig.json — skipping tsc"
fi

# Tests (best-effort)
npm test --silent 2>&1 | tee -a "$OUTDIR/test.log" || true

# Build (if defined)
if grep -q '"build"' package.json 2>/dev/null; then
  npm run build 2>&1 | tee -a "$OUTDIR/build.log" || true
else
  safe_append "$OUTDIR/build.log" "No build script in package.json"
fi

# Grep-like checks for debug markers
if command -v grep >/dev/null 2>&1; then
  grep -RIn --exclude-dir=node_modules -E "TODO:|FIXME|console\.log\(|debugger;|@ts-ignore|eslint-disable" . || true >> "$OUTDIR/code-warnings.txt"
fi

# Node-based simple secret heuristic
node -e "const fs=require('fs'),p=require('path'),re=/(API_KEY|SECRET|PASSWORD|ACCESS_TOKEN|PRIVATE_KEY|AKIA|BEGIN RSA PRIVATE KEY)/i; (function w(d){try{fs.readdirSync(d).forEach(f=>{const fp=p.join(d,f); try{const s=fs.statSync(fp); if(s.isDirectory()&&f!=='node_modules'&&f!=='.git') w(fp); if(s.isFile()){try{const c=fs.readFileSync(fp,'utf8'); if(re.test(c)) console.log(fp)}catch(e){}}}catch(e){}})}catch(e){}})('$FRONTEND_DIR/src');" > "$OUTDIR/secrets.txt" 2>/dev/null || true

# npm audit/outdated
npm audit --json > "$OUTDIR/npm_audit.json" 2>/dev/null || true
npm outdated --json > "$OUTDIR/npm_outdated.json" 2>/dev/null || true

# Zip up outputs (create zip next to project root)
ZIPNAME="$ROOT_DIR/audit-report-$TIMESTAMP.zip"
cd "$ROOT_DIR"
zip -r "$ZIPNAME" "audit-output/$TIMESTAMP" > /dev/null 2>&1 || true

safe_append "$OUTDIR/summary.txt" "Audit finished. ZIP: $ZIPNAME"
echo "Audit complete. Report: $ZIPNAME"
echo "Logs and artifacts in: $OUTDIR"
