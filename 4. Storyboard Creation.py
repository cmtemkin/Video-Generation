import sys
import zipfile
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except Exception:
    raise SystemExit("openai package not installed")

IMAGE_DIR = Path("data/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def main(script_path: str, n_images: int = 5):
    script_text = Path(script_path).read_text()
    img_paths = []
    for i in range(n_images):
        prompt = f"{script_text}\nScene {i+1}"
        resp = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
        )
        url = resp.data[0].url
        img_data = requests.get(url).content
        img_path = IMAGE_DIR / f"scene_{i+1:03d}.png"
        img_path.write_bytes(img_data)
        img_paths.append(img_path)
        print("Saved", img_path)
    zip_path = IMAGE_DIR / "images.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        for p in img_paths:
            z.write(p, p.name)
    print("ZIP saved", zip_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 4. Storyboard Creation.py <script_path> [num_images]")
        raise SystemExit(1)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    main(sys.argv[1], n)
