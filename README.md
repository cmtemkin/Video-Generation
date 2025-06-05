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

1. **Create a Python environment** (Python 3.8+):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   The pipeline also relies on `ffmpeg` being available on your system.
3. **Set up credentials** by copying `.env.example` to `.env` and adding your
   OpenAI API key.
4. **Try the command‑line orchestrator** to run a step or the whole pipeline:
   ```bash
   python orchestrate.py step 1  # run script 1 only
   python orchestrate.py all     # run all scripts sequentially
   ```
5. **Launch the graphical orchestrator**:
   ```bash
   python gui_orchestrator.py
   ```
   Select a step from the drop‑down or click **Run All**. Step 1 fields
   correspond to the prompts normally asked on the command line.
