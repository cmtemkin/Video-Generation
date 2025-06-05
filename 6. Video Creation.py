import sys
import zipfile
import shutil
from uuid import uuid4
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    import moviepy.editor as mp
except Exception:
    raise SystemExit("moviepy package not installed")

AUDIO_DIR = Path("data/audio")
IMAGE_DIR = Path("data/images")
FINAL_DIR = Path("data/final")

for d in [AUDIO_DIR, IMAGE_DIR, FINAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def main(audio_file: str, images_zip: str):
    audio_path = AUDIO_DIR / "narration.mp3"
    if Path(audio_file) != audio_path:
        shutil.copy(audio_file, audio_path)

    tmp_dir = IMAGE_DIR / f"temp_{uuid4().hex[:8]}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(images_zip) as z:
        z.extractall(tmp_dir)

    clips = []
    for img_file in sorted(tmp_dir.glob("*.png")):
        clip = mp.ImageClip(str(img_file)).resize(height=1080)
        if clip.w > 1920:
            clip = clip.crop(x_center=clip.w / 2, width=1920)
        else:
            clip = clip.resize(width=1920)
        clips.append(clip.set_duration(3))

    video = mp.concatenate_videoclips(clips, method="compose")
    audio = mp.AudioFileClip(str(audio_path))
    final_duration = min(video.duration, audio.duration)
    video = video.set_audio(audio.subclip(0, final_duration)).set_duration(final_duration)

    out_path = FINAL_DIR / "final_video.mp4"
    video.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac")
    shutil.rmtree(tmp_dir)
    print("Saved final video to", out_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python 6. Video Creation.py <audio_file> <images_zip>")
        raise SystemExit(1)
    main(sys.argv[1], sys.argv[2])
