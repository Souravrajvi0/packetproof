# PacketProof benchmarks (measured)

## Full pipeline — OpenRouter (primary, Oct 24, 2026)

Command (`.env` with `OPENROUTER_API_KEY`):

```bash
PYTHONPATH=. python3.11 evaluation/evaluate.py
```

| Metric | Value |
|--------|-------|
| Provider | `openrouter` |
| Model | `google/gemma-3-4b-it` |
| Requirements extracted | 11 |
| Findings total | 11 |
| Verified | 2 |
| Missing | 0 |
| Needs review | 9 |
| Not applicable | 0 |
| Contradictions | 1 |
| Planted issues detected | 5 / 5 |
| Planted issues detection rate | 1.0 |
| False-positive proxy | 0 |
| Requirements classified rate | 1.0 |
| Analysis duration | 41.13 s |
| Wall clock | 41.13 s |

Planted issue IDs (all `detected: true`): ISSUE-001 … ISSUE-005.

Raw output: `evaluation/results/latest.json` (gitignored).

## Ollama smoke test — CPU-only EC2

| Step | Result | Wall time |
|------|--------|-----------|
| `ollama pull gemma3:4b` | Success | ~30 s download |
| Requirement extraction only (Meridian PDF) | 11 requirements | **792.8 s (~13.2 min)** |

Full `evaluate.py` via Ollama on this VM previously hit **request timeouts**; use OpenRouter or a GPU machine for end-to-end local benchmarks.
