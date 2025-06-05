import sys
import requests
from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except Exception:
    raise SystemExit("openai package not installed")

FINAL_DIR = Path("data/final")
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def main(script_path: str):
    script = Path(script_path).read_text()
    resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Suggest 5 catchy titles for: {script}"}],
    )
    titles = [t.strip() for t in resp.choices[0].message.content.splitlines() if t.strip()]
    for i, t in enumerate(titles, 1):
        print(f"{i}. {t}")
    title = titles[int(input("Choose title number: ")) - 1]

    desc_resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Write a YouTube description for the video titled: {title}"}],
    )
    description = desc_resp.choices[0].message.content.strip()

    (FINAL_DIR / "title.txt").write_text(title)
    (FINAL_DIR / "description.txt").write_text(description)

    img_resp = openai.images.generate(
        model="dall-e-3",
        prompt=f"YouTube thumbnail for {title}",
        n=1,
        size="1024x1024",
    )
    img_url = img_resp.data[0].url
    img_data = requests.get(img_url).content
    img_path = FINAL_DIR / "cover.png"
    img_path.write_bytes(img_data)
    print("Saved metadata in", FINAL_DIR)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 5. Title, Description & Cover.py <script_path>")
        raise SystemExit(1)
    main(sys.argv[1])
