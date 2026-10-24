# Inference options

PacketProof supports two **Gemma 3 4B** backends:

## Ollama (local)

- Model tag: `gemma3:4b`
- Setup: `ollama pull gemma3:4b`
- Privacy: extracted PDF text stays on your machine

## OpenRouter (hosted)

- Model ID: `google/gemma-3-4b-it` (optional `:free` variant)
- Setup: `OPENROUTER_API_KEY` in `.env`
- Privacy: document text is sent to OpenRouter and their providers
- Speed: often much faster on CPU-only VMs

Set optional default in `.env`:

```bash
PACKETPROOF_INFERENCE=openrouter   # or ollama
```

The Streamlit sidebar always lets you switch providers per session.
