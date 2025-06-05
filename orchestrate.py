import subprocess
from pathlib import Path
import typer
from dotenv import load_dotenv

app = typer.Typer(help="Run the TLDR Studios pipeline")

SCRIPTS = [
    "1. Ideation & Script Gen.py",
    "2. Audio Creation.py",
    "3. Timestamp Transcription.py",
    "4. Storyboard Creation.py",
    "5. Title, Description & Cover.py",
    "6. Video Creation.py",
]

DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "inputs"
AUDIO_DIR = DATA_DIR / "audio"
IMAGE_DIR = DATA_DIR / "images"
FINAL_DIR = DATA_DIR / "final"

for d in [INPUT_DIR, AUDIO_DIR, IMAGE_DIR, FINAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def latest_file(path: Path, pattern: str) -> Path | None:
    files = sorted(path.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def run_step1():
    subprocess.run(["python", SCRIPTS[0]], check=True)


def run_step2():
    script = latest_file(INPUT_DIR, "*.txt")
    if not script:
        raise typer.Exit("No script found in data/inputs")
    subprocess.run(["python", SCRIPTS[1], str(script)], check=True)


def run_step3():
    audio = AUDIO_DIR / "tts_output.mp3"
    if not audio.exists():
        raise typer.Exit("Audio file not found. Run step 2 first.")
    subprocess.run(["python", SCRIPTS[2], str(audio)], check=True)


def run_step4(n: int = 5):
    script = latest_file(INPUT_DIR, "*.txt")
    if not script:
        raise typer.Exit("No script found in data/inputs")
    subprocess.run(["python", SCRIPTS[3], str(script), str(n)], check=True)


def run_step5():
    script = latest_file(INPUT_DIR, "*.txt")
    if not script:
        raise typer.Exit("No script found in data/inputs")
    subprocess.run(["python", SCRIPTS[4], str(script)], check=True)


def run_step6():
    audio = AUDIO_DIR / "tts_output.mp3"
    images_zip = IMAGE_DIR / "images.zip"
    if not audio.exists() or not images_zip.exists():
        raise typer.Exit("Audio or images not found. Run previous steps first.")
    subprocess.run(["python", SCRIPTS[5], str(audio), str(images_zip)], check=True)


@app.command()
def all(n_images: int = typer.Option(5, help="Number of images for storyboard")):
    """Run all scripts sequentially"""
    load_dotenv()
    run_step1()
    run_step2()
    run_step3()
    run_step4(n_images)
    run_step5()
    run_step6()


@app.command()
def step(n: int = typer.Argument(..., help="Script number to run (1-6)"), n_images: int = typer.Option(5, help="Number of images for storyboard")):
    """Run a single numbered script"""
    load_dotenv()
    if n == 1:
        run_step1()
    elif n == 2:
        run_step2()
    elif n == 3:
        run_step3()
    elif n == 4:
        run_step4(n_images)
    elif n == 5:
        run_step5()
    elif n == 6:
        run_step6()
    else:
        raise typer.Exit("Invalid step number")


if __name__ == "__main__":
    app()
