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

def run_script(script: str):
    if not Path(script).exists():
        typer.echo(f"Script {script} not found")
        raise typer.Exit(1)
    typer.echo(f"\n=== Running: {script} ===\n")
    subprocess.run(["python", script], check=True)

@app.command()
def all():
    """Run all scripts sequentially"""
    load_dotenv()
    for script in SCRIPTS:
        run_script(script)

@app.command()
def step(n: int = typer.Argument(..., help="Script number to run (1-6)")):
    """Run a single numbered script"""
    load_dotenv()
    idx = n - 1
    if idx < 0 or idx >= len(SCRIPTS):
        typer.echo("Invalid script number")
        raise typer.Exit(1)
    run_script(SCRIPTS[idx])

if __name__ == "__main__":
    app()
