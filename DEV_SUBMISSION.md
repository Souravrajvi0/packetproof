# DEV.to draft — PacketProof

**Title:** PacketProof: local Gemma does the boring scholarship paperwork audit

**Tags:** `opensource`, `ai`, `python`, `hacktoberfest`, `gemma`

---

## The manual work PacketProof removes

Before submitting a scholarship or grant packet, applicants usually:

- Re-read a dense requirements PDF
- Match every bullet to files on disk
- Compare names, dates, and GPA across forms
- Check recommendation letter dates and signatures

That is repetitive, tiring, and easy to mess up under a deadline.

## Why that work is painful

One missing transcript or unsigned declaration can disqualify a strong candidate. Conflicting graduation dates look careless even when they are typos. Policy windows (e.g. “letter within six months”) are easy to overlook.

Humans are poor at exhaustive checklist labor. Models can help **only if** conclusions cite real evidence—not vibes.

## How PacketProof works

1. Upload the **instructions PDF** and **application PDFs**.
2. PyMuPDF extracts text (with warnings for image-only pages).
3. **Gemma 3 4B via Ollama** extracts atomic requirements with source quotes.
4. For each requirement, Gemma proposes evidence (file, page, excerpt).
5. A **Python verifier** checks that pages exist and quotes appear in extracted text.
6. A separate pass extracts fields and runs **deterministic** contradiction checks.
7. Streamlit shows verified / missing / needs review, an evidence inspector, and a downloadable HTML report.

No “approved” stamp—just what was found, what was not, and what needs human review.

## Why Gemma and open-source AI

Application packets contain PII. Shipping them to a hosted API is often unacceptable.

**Gemma** through **Ollama** gives private, local inference, no per-document API fees, and the freedom to change models. That matches Hacktoberfest **Slow and Steady**: let local AI do the lazy-person’s document cross-check.

## Demonstration

```bash
pip install -r requirements.txt
ollama pull gemma3:4b
python3.11 demo/generate_samples.py
streamlit run app.py
```

Upload the Meridian Future Scholars demo PDFs. The pipeline is real—results are not hardcoded from `demo/answer_key.json`.

## Measured results

**On the cloud build VM:** 15 unit tests passed; Ollama was not available, so **no end-to-end inference benchmark** was recorded there.

**On your machine**, after Ollama is running:

```bash
PYTHONPATH=. python3.11 evaluation/evaluate.py
```

Report `planted_issues_detected`, `false_positive_proxy`, and `analysis_duration_seconds` from `evaluation/results/latest.json`. Publish only numbers you actually measured.

## Known failures

- Scanned PDFs without text layers need OCR (not in MVP).
- Invented model quotes are caught and downgraded to **Needs review**.
- Semantic matching can confuse similar document types.

## Lessons learned

1. A **verification layer** between the model and the user is essential.
2. **Conservative copy** (“evidence not found”) beats false confidence.
3. One Gemma call per requirement is simple to debug but not fast—batching is the next step.

## Screenshots

Add Streamlit screenshots from your local run before publishing.

## Repository

`<your-github-url>/packetproof`
