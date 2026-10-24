# DEV.to — PacketProof (Hacktoberfest draft)

**Title:** PacketProof: Gemma 3 4B checks your scholarship packet—with PDF receipts

**Tags:** `#hacktoberfest` `#opensource` `#ai` `#python` `#gemma`

---

## Problem

Application packets are checklist hell: transcripts, signatures, date windows, GPA. I built **PacketProof** to cross-check requirements against uploads automatically—with **evidence**, not vibes.

## Open-weight Gemma, your choice where it runs

PacketProof uses **Google Gemma 3 4B** end-to-end:

- **Ollama (`gemma3:4b`)** — local, private, perfect for Hacktoberfest’s local-AI theme  
- **OpenRouter (`google/gemma-3-4b-it`)** — same model family, hosted—great when your laptop/VM can’t run 4B on CPU  

You pick in the sidebar. The **verification pipeline** (quote + page checks) is identical.

## Why not just ChatGPT?

Every finding links to instruction quotes and document excerpts. Python verifies pages and text before “verified” sticks. Hallucinated citations → **needs review**.

![PacketProof](docs/screenshots/streamlit_home.png)

**Video beats:** upload → analyze → **Evidence inspector** (contradiction or GPA) → HTML export (`docs/VIDEO_STORYBOARD.md`).

## Honest metrics (Meridian demo)

| Metric | Result |
|--------|--------|
| Planted issue recall | **60%** (3/5) |
| Planted issue precision | **33%** |
| Analysis time | **~41 s** (hosted Gemma 3 4B) |

We dropped inflated keyword-based “5/5” scores for structured matching—see `evaluation/planted_match.py`.

## Try it

https://github.com/Souravrajvi0/packetproof

```bash
pip install -r requirements.txt
ollama pull gemma3:4b          # local path
# or OPENROUTER_API_KEY in .env  # cloud path
streamlit run app.py
```

## Best Use of Gemma

Open-weight Gemma is the core—not a thin API wrapper—with optional **local** inference for privacy-first users.
