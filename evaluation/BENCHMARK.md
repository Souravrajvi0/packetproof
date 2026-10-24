# PacketProof benchmarks (measured)

Environment: AWS EC2 **CPU-only** (no GPU), `gemma3:4b` via Ollama, Oct 24, 2026.

## Verified end-to-end inference

| Step | Result | Wall time |
|------|--------|-----------|
| Ollama + `gemma3:4b` pull | Success | ~30s download |
| Requirement extraction (Meridian demo PDF) | **11 requirements** extracted | **792.8 s (~13.2 min)** |
| Full `evaluate.py` (entire pipeline) | **In progress / long-running on CPU** | Expect **1–3+ hours** (many sequential LLM calls) |

Smoke command (reproducible):

```bash
PYTHONPATH=. python3.11 -c "
from pathlib import Path
from core.llm_client import OllamaClient
from core.pdf_processor import extract_pdf_from_bytes
from core.requirements import extract_requirements
doc = extract_pdf_from_bytes('meridian_requirements_2026.pdf', Path('demo/samples/meridian_requirements_2026.pdf').read_bytes())
print(len(extract_requirements(doc, OllamaClient(timeout=1800.0))))
"
```

## Full evaluation

```bash
PYTHONPATH=. python3.11 evaluation/evaluate.py
```

Uses `OllamaClient(timeout=1800.0)` per request. On a machine with a GPU, times are typically much lower.

Results file: `evaluation/results/latest.json` (gitignored; not committed).

## First failed run

An earlier run failed with `Ollama request timed out` at the default **300s** client timeout. Timeout was increased to **1200s** default / **1800s** in `evaluate.py`.
