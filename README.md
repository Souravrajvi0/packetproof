# PacketProof

**Catch application mistakes before they cost you.**

PacketProof is a privacy-first application inspector. Upload instruction and application PDFs; local [Gemma 3 4B](https://ollama.com/library/gemma3) via Ollama extracts requirements, matches evidence, and produces an evidence-backed readiness report without cloud AI APIs.

## Quick start

```bash
cd packetproof
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull gemma3:4b
python3.11 demo/generate_samples.py
streamlit run app.py
```

## Tests

```bash
PYTHONPATH=. python3.11 -m pytest
```

## Evaluation

```bash
PYTHONPATH=. python3.11 evaluation/evaluate.py
```

## Privacy

All inference is local via Ollama. Uploads stay in session memory; use **Clear session** to discard.

See full documentation in-repo for architecture, demo scenario, and limitations.

## License

MIT
