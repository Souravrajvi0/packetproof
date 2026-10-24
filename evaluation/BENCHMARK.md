# PacketProof benchmarks (measured)

## Full pipeline — Gemma 3 4B (evaluation harness)

Public docs assume **Ollama (`gemma3:4b`)**. Numbers below from one Gemma 3 4B run of `evaluate.py`.

```bash
PYTHONPATH=. python3.11 evaluation/evaluate.py
```

Last run: Oct 24, 2026.

| Metric | Value |
|--------|-------|
| Analysis duration | 40.71 s |
| Requirements extracted | 11 |
| Verified / missing / needs review | 2 / 0 / 9 |
| Contradictions | 1 |
| **Planted issue recall** | **0.6** (3/5) |
| **Planted issue precision** | **0.333** |
| False-positive findings (non-planted topics flagged) | 6 |

### Per planted issue

| ID | Matched | Notes |
|----|---------|-------|
| ISSUE-001 | No | REQ-002 transcript → needs_review, wording did not meet “missing” rules |
| ISSUE-002 | Yes | CON-001 graduation dates 2024 vs 2025 |
| ISSUE-003 | No | REQ-004 recommendation → **verified** (false confidence) |
| ISSUE-004 | Yes | REQ-009 signature / declaration |
| ISSUE-005 | Yes | REQ-006 GPA eligibility |

Evaluation logic: `evaluation/planted_match.py` (not serialized-report keywords).

## Ollama on CPU-only EC2

Requirement extraction only: **11** requirements in **~792 s**. Full local pipeline not benchmarked end-to-end on that hardware.
