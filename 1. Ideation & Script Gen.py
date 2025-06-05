import os
import textwrap
from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except Exception:
    raise SystemExit("openai package not installed")

MODEL = "gpt-4o"
DATA_DIR = Path("data/inputs")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def chat(prompt: str, temperature: float = 0.8) -> str:
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def main():
    cats = [c.strip() for c in chat("Suggest faceless YouTube categories about tech trends", 0.6).splitlines() if c.strip()]
    for i, c in enumerate(cats, 1):
        print(f"{i}. {c}")
    category = cats[int(input("Pick a category number: ")) - 1]

    ideas = [i.strip() for i in chat(f"Give 5 video ideas about {category}").splitlines() if i.strip()]
    for i, idea in enumerate(ideas, 1):
        print(f"{i}. {idea}")
    idea = ideas[int(input("Pick an idea number: ")) - 1]

    script = chat(f"Write a short narration for: {idea}")
    print("\n--- Script ---\n")
    print(textwrap.fill(script, 80))

    filename = DATA_DIR / f"{slugify(idea)[:50]}.txt"
    filename.write_text(script, encoding="utf-8")
    print("Saved", filename)


if __name__ == "__main__":
    main()
