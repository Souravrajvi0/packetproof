# Optional cloud inference (maintainers / CI only)

Hacktoberfest submission path is **local Gemma via Ollama** (`gemma3:4b`).

For slow CPU VMs or automated benchmarks, maintainers may set in `.env` (gitignored):

```bash
PACKETPROOF_INFERENCE=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
```

This uses the same **Gemma 3 4B** weights through a hosted OpenAI-compatible API. **Do not use for sensitive real applicant data** unless you accept third-party processing.

Not required for judges or end users. Public docs and DEV posts describe **Ollama only**.
