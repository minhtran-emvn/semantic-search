# Performance Results

## Environment

- Backend: Docker container (`semantic-audio-backend`) on CPU
- Translation: googletrans (Python library)
- Embeddings: Copied from `backend/data/embeddings` into `/data/embeddings`
- Test runner: `python3 backend/scripts/performance_test.py --runs 5`
- Date: 2026-01-21

## Baseline Measurements

| Scenario | Avg (ms) | Median (ms) | P95 (ms) | Runs |
| --- | ---: | ---: | ---: | ---: |
| English query | 309.9 | 293.8 | 453.9 | 5 |
| Non-English query | 303.0 | 275.3 | 397.1 | 5 |
| Content type toggle re-search | 210.3 | 202.8 | 301.9 | 5 |

Notes:
- English vs non-English latency was comparable in this run; translation overhead was not dominant under current load.
- Toggle re-search remained under the 500ms target in this baseline.

## Profiling Summary (cProfile)

Command:
```
python3 -m cProfile -s cumtime backend/scripts/performance_test.py --runs 3
```

Top cumulative time (client side):
- `urllib.request.urlopen` and socket reads dominated (>95%), indicating most time spent waiting on backend responses.
- This suggests backend work (translation + CLAP embedding + FAISS search) is the primary latency driver.

## Bottleneck Analysis (Qualitative)

1. **CLAP text embedding generation** (model inference on CPU) is likely the largest backend cost per request.
2. **Translation API call** contributes to non-English queries, but was not a visible outlier in baseline.
3. **FAISS search** is fast relative to embedding and translation steps.

## Follow-up

- Run frontend DevTools performance capture once UI is exercised in a browser.
- Re-run baseline after translation caching and other optimizations are applied.
