# GX10 FlashNext production recipe

This is the reproducible handoff for the exact production model path used by
one ASUS GX10 / NVIDIA GB10 (128 GB unified memory). It is intentionally a
small control repository: no model weights, Hugging Face cache, Docker image,
runtime state, DSH sessions, or credentials are committed.

## What this deploys

| Component | Production value |
| --- | --- |
| Model checkpoint | [`Saren/Qwen3.8-Flash-Next-W4A16-AutoRound-hybrid`](https://huggingface.co/Saren/Qwen3.8-Flash-Next-W4A16-AutoRound-hybrid) at `8b82f0b7abe3d1150a7827d298c75e86267636ae` |
| PLE table | [`Saren/Qwen3.8-Flash-Next-ple-table-fp8`](https://huggingface.co/Saren/Qwen3.8-Flash-Next-ple-table-fp8) at `50511b0a41aa1d34b8beb7e5d4bb06a0b650dc14` |
| Engine | vLLM `0.1.dev20073+g8e685d198`, image `gx10-qwen38-flash-next-lab:autoround-mtp3` |
| Context / scheduler | 262,144 tokens; 8 sequences; chunked prefill 8,192 |
| KV / speculation | 20 GiB KV; BF16/auto KV; vLLM MTP with 3 speculative tokens |
| PLE / precision | FP8 PLE mmap from local NVMe; AutoRound W4A16 experts with FP8 side layers |
| Cache | vLLM prefix cache enabled with Mamba alignment; stock `persistent_topk` |
| API | loopback `127.0.0.1:8019/v1`; optional loopback policy proxy `:8021/v1` |

The model is not a Git artifact. Download the two pinned Hugging Face artifacts
with `scripts/fetch-artifacts.sh`; respect the upstream model license and any
access requirements before downloading.

## What is ours versus upstream

The model implementation and primary image build come from the pinned
[Saren AutoRound recipe](https://github.com/Saren-Arterius/qwen3.8-Flash-DGX-AutoRound)
at commit `01c5914f322716b39fd71d5584ed800955582e65`. Build the image from that
source using the included launcher patch. That upstream Dockerfile carries the
model-specific PLE mmap, GB10 FLA, hybrid-precision, Mamba-state, and prefix
cache changes.

This repository contains the small lab-owned parts that make the production
path practical: the fixed runtime contract, artifact fetch/verification,
bounded post-start warmup, deterministic-default transparent proxy, systemd
templates, benchmark evidence, and the local launcher patch. It does not claim
to replace vLLM kernels or alter model weights.

## Rebuild on another GX10

Use Ubuntu/DGX OS on a single GB10 (`sm_121`), Docker with NVIDIA runtime,
recent NVIDIA driver, Python 3, Git, and Hugging Face CLI. Keep the raw model
API loopback-only.

```bash
git clone git@github.com:jfxmedia/gx10-flashnext-production.git
cd gx10-flashnext-production
cp config/production.env.example .env
# Edit MODEL_DIR and TABLE_DIR in .env for local NVMe storage.
bash scripts/fetch-artifacts.sh .env
bash scripts/build-image.sh
bash scripts/run-production.sh .env
curl -fsS http://127.0.0.1:8019/v1/models
python3 scripts/warmup_endpoint.py --output /tmp/flashnext-warmup.json
```

`build-image.sh` clones the pinned upstream recipe, checks out the exact
commit, applies `patches/saren-launcher-production.patch`, then builds the
image. Treat a failed patch or a changed upstream source as a stop condition,
not a reason to silently use a different recipe.

For persistent operation, copy the two templates in `systemd/` after replacing
`/srv/gx10-flashnext-production` with the checkout path. The proxy defaults
only omitted sampling fields to `temperature=0`, `top_p=1`, and `top_k=-1`; it
does not alter explicit caller choices or log prompt/completion bodies.

## Verification and safety

- Run on an idle host for benchmarks; do not use a live DSH session as a clean
  benchmark fixture.
- Never bind raw port 8019 to the LAN or internet. Use a separate authenticated
  private proxy/Tailscale path if remote clients require access.
- Do not enable FP8 KV or unpromoted exact-top-k experiments as defaults; they
  are not the active production configuration.
- Do not copy model data, `.env`, cache folders, logs, or DSH state into Git.

See [the benchmark record](docs/BENCHMARKS.md) and the machine-readable
[recipe](recipe/autoround-mtp3.toml) before changing a setting.
