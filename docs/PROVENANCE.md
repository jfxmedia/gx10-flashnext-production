# Provenance and reproducibility boundary

Observed on 2026-09-02 from the running production container:

- container/image: `flashnext-autoround-mtp3-exp` / `gx10-qwen38-flash-next-lab:autoround-mtp3`
- image digest: `sha256:d28ffb1cdca3c5f341668e78a1e18ad4fdbe3fc791d788dce24a1ce6f3c34ac7`
- vLLM: `0.1.dev20073+g8e685d198`
- host: NVIDIA GB10, `sm_121`, 128 GB unified memory, aarch64; driver `580.173.02`
- checkpoint index: 17 shards, 123,958,298,771 parameters, 175,330,224,632 bytes

The artifact and source references are intentionally pinned in the recipe.
Each replacement must record new hashes and rerun functional, long-context,
tool-call, and repeatability gates before it is presented as production.

The current QSA selector is the stock `persistent_topk`; the manifest used by
the former laboratory contains an aspirational exact-top-k label, but no exact
selector is active in this production container. That distinction is important
when comparing performance and determinism reports.
