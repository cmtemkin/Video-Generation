# 🎬 TL;DR Studios — Text‑to‑Video Pipeline

**TL;DR Studios** turns raw text ideas into ready‑to‑publish videos.  
Every processing stage lives in its own numbered Python script (already included in this repo), making the workflow transparent, hackable, and easy to automate.

> **Two ways to work**  
> • **Step‑by‑step (interactive)** — run one script at a time, review outputs, tweak, re‑run.  
> • **Fully automated (future state)** — one Orchestrator ties everything together, pushes status updates, and drops a finished `.mp4`, thumbnail, and SEO copy in your inbox.

---

## 📂 Repo Structure

tldr‑studios/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│ ├── inputs/ ← raw text files
│ ├── audio/ ← WAV narration
│ ├── transcripts/ ← timestamp CSVs
│ ├── images/ ← storyboard stills
│ ├── clips/ ← motion clips
│ └── final/ ← title+desc .txt, cover .png, video .mp4
├── 1. Ideation & Script Gen.py
├── 2. Audio Creation.py
├── 3. Timestamp Transcription.py
├── 4. Storyboard Creation.py
├── 5. Title, Description & Cover.py
├── 6. Video Creation.py
└── orchestrate.py ← (road‑map) one‑click pipeline runner

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your OpenAI key.
3. Run a single step or the entire pipeline:
   ```bash
   python orchestrate.py step 1  # run script 1
   python orchestrate.py all     # run all scripts
   ```

4. Launch the Streamlit wizard:
   ```bash
   streamlit run app.py
   ```

