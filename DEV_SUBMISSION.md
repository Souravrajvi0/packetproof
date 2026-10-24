# DEV.to — PacketProof (Hacktoberfest Week 3 draft)

**Title:** PacketProof: local Gemma catches scholarship mistakes—with PDF receipts

**Tags:** `#hacktoberfest` `#opensource` `#ai` `#python` `#gemma`

**Category:** Best Use of Gemma

---

## The boring work nobody wants to do

Before you submit a scholarship packet, you re-read a long requirements PDF and cross-check every file: transcript, signatures, recommendation dates, GPA floors. One miss can disqualify you. I built **PacketProof** to automate that checklist.

## Slow and Steady (local AI)

PacketProof runs **Google Gemma 3 4B locally via Ollama**. Your PDFs stay on your machine. No paid chat API. Open-weight Gemma is the engine—not decoration—because application data is sensitive and document review is repetitive work AI should absorb.

## How it’s different from a chatbot

Every finding ties to **evidence**: instruction quote, candidate filename, page, and excerpt. A Python layer checks that pages exist and quotes appear in extracted text before anything is “verified.” If the model hallucinates a citation, the UI says **needs review**—not “you’re approved.”

![PacketProof](docs/screenshots/streamlit_home.png)

**Demo flow (record this for video):**

1. Upload Meridian demo requirements + application PDFs  
2. Analyze with **Ollama + gemma3:4b**  
3. Open **Evidence inspector** — show graduation contradiction or GPA finding with quotes  
4. Download HTML report  

Storyboard: `docs/VIDEO_STORYBOARD.md`

## Honest benchmark (Meridian demo)

Structured evaluation (`evaluation/planted_match.py`):

| Metric | Result |
|--------|--------|
| Planted issue recall | **60%** (3/5) |
| Planted issue precision | **33%** |
| Analysis time | **~41 s** on Gemma 3 4B |

We fixed an earlier inflated “5/5” score that used loose keyword matching. Real recall is lower—that’s the point of measuring properly.

## Limitations

- Text PDFs only; no OCR yet  
- “Needs review” is common (conservative by design)  
- Recommendation letter was once **verified** when it should have been flagged—shows why humans still matter  

## Try it

https://github.com/Souravrajvi0/packetproof

```bash
pip install -r requirements.txt
ollama pull gemma3:4b
streamlit run app.py
```

## Best Use of Gemma

Local **gemma3:4b** + evidence validation = private, portable, open-source document review for real application packets.
