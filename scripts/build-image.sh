#!/usr/bin/env bash
set -euo pipefail
VENDOR_DIR=${1:-vendor/qwen3.8-Flash-DGX-AutoRound}
git clone https://github.com/Saren-Arterius/qwen3.8-Flash-DGX-AutoRound.git "$VENDOR_DIR"
git -C "$VENDOR_DIR" checkout 01c5914f322716b39fd71d5584ed800955582e65
git -C "$VENDOR_DIR" apply "$(cd "$(dirname "$0")/.." && pwd)/patches/saren-launcher-production.patch"
docker build -t gx10-qwen38-flash-next-lab:autoround-mtp3 "$VENDOR_DIR"
