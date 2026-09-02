#!/usr/bin/env bash
set -euo pipefail
. "${1:-.env}"
: "${MODEL_DIR:?MODEL_DIR is required}" "${TABLE_DIR:?TABLE_DIR is required}"
test -f "$MODEL_DIR/config.json"
test -d "$TABLE_DIR"
SPLIT='["vllm::unified_attention_with_output","vllm::unified_mla_attention_with_output","vllm::mamba_mixer2","vllm::mamba_mixer","vllm::short_conv","vllm::qwen3_8_flash_next_ple_short_conv","vllm::qwen3_8_flash_next_qsa_with_output","vllm::linear_attention","vllm::qwen_gdn_attention_core","vllm::qwen_gdn_attention_core_fused_norm_packed","vllm::sparse_attn_indexer","vllm::ple_mmap_lookup"]'
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" --restart unless-stopped --gpus all --ipc=host --shm-size 16g \
  -p "$BIND_HOST:$PORT:8000" -v "$MODEL_DIR:/model:ro" -v "$TABLE_DIR:/ple-table:ro" \
  -e VLLM_PLE_MMAP=1 -e VLLM_PLE_MMAP_WORKERS=32 -e VLLM_PLE_MMAP_PREWARM="$PREWARM" \
  -e VLLM_PLE_MMAP_PREFETCH="$PLE_PREFETCH" -e VLLM_PLE_MMAP_MADV_RANDOM="$PLE_MADV_RANDOM" \
  -e VLLM_DISABLE_EAGLE_BLOCK_DROP="$VLLM_DISABLE_EAGLE_BLOCK_DROP" -e VLLM_PLE_MMAP_DIR=/ple-table \
  -e VLLM_MARLIN_USE_ATOMIC_ADD=1 -e VLLM_FP8_HYBRID="$FP8_HYBRID" -e VLLM_QSA_EXACT_TOPK="$VLLM_QSA_EXACT_TOPK" \
  -e VLLM_USE_DEEP_GEMM=0 -e VLLM_USE_FLASHINFER_SAMPLER=1 "$IMAGE" /model \
  --served-model-name "$SERVED_NAME" --host 0.0.0.0 --port 8000 --load-format fastsafetensors \
  --max-model-len "$CTX" --max-num-seqs "$SEQS" --gpu-memory-utilization "$GPU_MEM" \
  --enable-prefix-caching --enable-chunked-prefill --max-num-batched-tokens "$BATCHED_TOKENS" \
  -cc.cudagraph_mode=PIECEWISE -cc.splitting_ops="$SPLIT" --no-enable-flashinfer-autotune \
  --kv-cache-dtype auto --kv-cache-memory-bytes "$KV_BYTES" --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder --reasoning-parser qwen3 \
  --speculative-config "{\"method\":\"mtp\",\"num_speculative_tokens\":$MTP}"
