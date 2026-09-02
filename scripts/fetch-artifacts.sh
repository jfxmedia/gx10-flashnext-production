#!/usr/bin/env bash
set -euo pipefail
. "${1:-.env}"
MODEL_REPO=Saren/Qwen3.8-Flash-Next-W4A16-AutoRound-hybrid
MODEL_REV=8b82f0b7abe3d1150a7827d298c75e86267636ae
TABLE_REPO=Saren/Qwen3.8-Flash-Next-ple-table-fp8
TABLE_REV=50511b0a41aa1d34b8beb7e5d4bb06a0b650dc14
mkdir -p "$MODEL_DIR" "$TABLE_DIR"
hf download "$MODEL_REPO" --revision "$MODEL_REV" --local-dir "$MODEL_DIR" --max-workers 8
hf download "$TABLE_REPO" --revision "$TABLE_REV" --local-dir "$TABLE_DIR" --max-workers 8
hf cache verify "$MODEL_REPO" --revision "$MODEL_REV" --local-dir "$MODEL_DIR" --fail-on-missing-files
hf cache verify "$TABLE_REPO" --revision "$TABLE_REV" --local-dir "$TABLE_DIR" --fail-on-missing-files
