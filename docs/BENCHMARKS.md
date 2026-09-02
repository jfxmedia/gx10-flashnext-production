# Production measurements

All values are one GB10 / GX10. Do not compare values across different model artifacts, contexts, concurrency, cache states, or metric definitions.

| Run | Workload | Output rate |
| --- | --- | ---: |
| Live DSH session, 2026-09-02 | 41 completed requests; 27m30s active time | **49.16 tok/s mean** (21.60–60.90) |
| AutoRound hybrid MTP3, 2026-08-31 | clean c1, 256 generated tokens | **53.47 tok/s** |
| AutoRound hybrid MTP3, 2026-08-31 | clean c2 aggregate | **87.45 tok/s** |
| AutoRound hybrid MTP2, 2026-08-31 | clean c1 / c2 aggregate | 46.03 / 67.19 tok/s |
| PLE-prefetch canary | clean c1 / c2 aggregate | 32.87 / 54.36 tok/s |
| Historical FlashNext R9 | clean c1 | 26.81 tok/s |
| Historical Qwen3.8-27B DFlash2 | 8k controlled run | about 30 tok/s |

The live window had mean speculative acceptance length 3.36 and draft acceptance 78.71%; GPU KV use averaged 12.62%, prefix-cache hits 96.65%, and multimodal-cache hits 98.10%. The in-flight request was excluded.
