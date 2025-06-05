import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except Exception:
    raise SystemExit("openai package not installed")

AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def main(text_file: str):
    text = Path(text_file).read_text()
    resp = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        speed=0.95,
    )
    out_path = AUDIO_DIR / "tts_output.mp3"
    resp.stream_to_file(str(out_path))
    print("Saved", out_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 2. Audio Creation.py <text_file>")
        raise SystemExit(1)
    main(sys.argv[1])
