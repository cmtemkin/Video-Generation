import os
import zipfile
from pathlib import Path
from uuid import uuid4
import shutil

import streamlit as st
import pandas as pd
import moviepy.editor as mp
import requests
from slugify import slugify
from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except Exception:
    openai = None


def get_key():
    key = st.session_state.get("OPENAI_API_KEY")
    if not key:
        key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    return key

if openai:
    key = get_key()
    if key:
        openai.api_key = key

DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "inputs"
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPT_DIR = DATA_DIR / "transcripts"
IMAGE_DIR = DATA_DIR / "images"
FINAL_DIR = DATA_DIR / "final"

for d in [INPUT_DIR, AUDIO_DIR, TRANSCRIPT_DIR, IMAGE_DIR, FINAL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

st.title("TL;DR Studios Wizard")

if openai and not openai.api_key:
    st.sidebar.warning("Enter your OpenAI API key to enable API features.")
    key_input = st.sidebar.text_input("OpenAI API Key", type="password")
    if key_input:
        openai.api_key = key_input
        st.session_state["OPENAI_API_KEY"] = key_input

step = st.sidebar.radio(
    "Step",
    [
        "1. Script Generation",
        "2. Audio Creation",
        "3. Transcription",
        "4. Storyboard",
        "5. Metadata & Cover",
        "6. Video Assembly",
    ],
)

# ----------------------------- Step 1 ---------------------------------
if step.startswith("1"):
    st.header("Step 1: Ideation & Script Generation")
    if not openai:
        st.error("openai package not available. Install dependencies.")
    else:
        category_prompt = st.text_input(
            "Prompt for categories",
            "Suggest faceless YouTube categories about tech trends",
        )
        if st.button("Generate Categories"):
            resp = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": category_prompt}],
            )
            cats = [c.strip() for c in resp.choices[0].message.content.splitlines() if c.strip()]
            st.session_state["categories"] = cats
        cats = st.session_state.get("categories")
        if cats:
            category = st.selectbox("Choose category", cats)
            idea_prompt = st.text_input("Prompt for ideas", f"Give 5 video ideas about {category}")
            if st.button("Generate Ideas"):
                resp = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": idea_prompt}],
                )
                ideas = [i.strip() for i in resp.choices[0].message.content.splitlines() if i.strip()]
                st.session_state["ideas"] = ideas
        ideas = st.session_state.get("ideas")
        if ideas:
            idea = st.selectbox("Choose idea", ideas)
            script_prompt = st.text_area("Script prompt", f"Write a short narration for: {idea}")
            if st.button("Generate Script"):
                resp = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": script_prompt}],
                )
                script = resp.choices[0].message.content.strip()
                st.session_state["script"] = script
        if st.session_state.get("script"):
            script = st.text_area("Script", st.session_state["script"])
            if st.button("Save Script"):
                filename = slugify(script[:50]) + ".txt"
                path = INPUT_DIR / filename
                path.write_text(script, encoding="utf-8")
                st.success(f"Saved {path}")
                st.session_state["script_path"] = str(path)

# ----------------------------- Step 2 ---------------------------------
elif step.startswith("2"):
    st.header("Step 2: Audio Creation")
    if not openai:
        st.error("openai package not available.")
    else:
        default_script = st.session_state.get("script", "")
        text = st.text_area("Narration text", default_script)
        if st.button("Generate Audio"):
            with st.spinner("Calling TTS..."):
                try:
                    response = openai.audio.speech.create(
                        model="gpt-4o-mini-tts",
                        voice="coral",
                        input=text,
                        speed=0.95,
                    )
                    audio_path = AUDIO_DIR / "tts_output.mp3"
                    st.session_state["audio_path"] = str(audio_path)
                    response.stream_to_file(str(audio_path))
                    st.audio(str(audio_path))
                    with open(audio_path, "rb") as f:
                        st.download_button("Download MP3", f, file_name="tts_output.mp3")
                except Exception as e:
                    st.error(f"TTS failed: {e}")

# ----------------------------- Step 3 ---------------------------------
elif step.startswith("3"):
    st.header("Step 3: Transcription")
    if not openai:
        st.error("openai package not available.")
    else:
        audio_file = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a"])
        if st.button("Transcribe") and audio_file is not None:
            path = AUDIO_DIR / "uploaded_audio"
            path.write_bytes(audio_file.read())
            client = openai.OpenAI()
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=open(path, "rb"),
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
            df = pd.DataFrame([{"word": w.word, "start": w.start, "end": w.end} for w in resp.words])
            csv_path = TRANSCRIPT_DIR / "sentence_timestamps.csv"
            st.session_state["transcript_csv"] = str(csv_path)
            df.to_csv(csv_path, index=False)
            st.dataframe(df.head())
            with open(csv_path, "rb") as f:
                st.download_button("Download CSV", f, file_name="sentence_timestamps.csv")

# ----------------------------- Step 4 ---------------------------------
elif step.startswith("4"):
    st.header("Step 4: Storyboard")
    if not openai:
        st.error("openai package not available.")
    else:
        script_text = st.text_area("Script text", st.session_state.get("script", ""))
        n_images = st.number_input("Number of scenes", min_value=1, max_value=20, value=5)
        if st.button("Generate Images"):
            IMAGE_DIR.mkdir(parents=True, exist_ok=True)
            img_paths = []
            for i in range(int(n_images)):
                prompt = f"{script_text}\nScene {i+1}" if script_text else f"Scene {i+1}"
                resp = openai.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                )
                img_url = resp.data[0].url
                img_data = requests.get(img_url).content
                img_path = IMAGE_DIR / f"scene_{i+1:03d}.png"
                img_path.write_bytes(img_data)
                img_paths.append(img_path)
                st.image(str(img_path))
            zip_path = IMAGE_DIR / "images.zip"
            st.session_state["images_zip"] = str(zip_path)
            with zipfile.ZipFile(zip_path, "w") as z:
                for p in img_paths:
                    z.write(p, p.name)
            with open(zip_path, "rb") as f:
                st.download_button("Download Images ZIP", f, file_name="images.zip")

# ----------------------------- Step 5 ---------------------------------
elif step.startswith("5"):
    st.header("Step 5: Metadata & Cover")
    if not openai:
        st.error("openai package not available.")
    else:
        script = st.text_area("Script", st.session_state.get("script", ""))
        if st.button("Suggest Titles"):
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Suggest 5 catchy titles for: {script}"}],
            )
            titles = [t.strip() for t in resp.choices[0].message.content.splitlines() if t.strip()]
            st.session_state["titles"] = titles
        titles = st.session_state.get("titles")
        if titles:
            title = st.selectbox("Choose title", titles)
            if st.button("Generate Description & Cover"):
                desc_resp = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Write a YouTube description for the video titled: {title}"}],
                )
                description = desc_resp.choices[0].message.content.strip()
                FINAL_DIR.mkdir(parents=True, exist_ok=True)
                (FINAL_DIR / "description.txt").write_text(description)
                with open(FINAL_DIR / "description.txt", "rb") as f:
                    st.download_button("Download Description", f, file_name="description.txt")
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
                st.image(str(img_path))
                with open(img_path, "rb") as f:
                    st.download_button("Download Cover", f, file_name="cover.png")
                (FINAL_DIR / "title.txt").write_text(title)

# ----------------------------- Step 6 ---------------------------------
elif step.startswith("6"):
    st.header("Step 6: Video Assembly")
    st.warning("This step requires moviepy and can be slow.")
    audio_file = st.file_uploader("Upload narration audio", type=["mp3", "wav"])
    images_zip = st.file_uploader("Upload storyboard ZIP", type=["zip"])
    if st.button("Assemble Video"):
        try:
            if audio_file:
                audio_path = AUDIO_DIR / "narration.mp3"
                audio_path.write_bytes(audio_file.read())
                st.session_state["audio_path"] = str(audio_path)
            elif st.session_state.get("audio_path"):
                st.info("Using audio from Step 2.")
                audio_path = Path(st.session_state["audio_path"])
            else:
                st.error("Please upload or generate an audio file.")
                st.stop()

            if images_zip:
                zip_path = IMAGE_DIR / "uploaded_images.zip"
                zip_path.write_bytes(images_zip.read())
                st.session_state["images_zip"] = str(zip_path)
            elif st.session_state.get("images_zip"):
                st.info("Using images from Step 4.")
                zip_path = Path(st.session_state["images_zip"])
            else:
                st.error("Please upload or generate storyboard images.")
                st.stop()

            tmp_dir = IMAGE_DIR / f"temp_{uuid4().hex[:8]}"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path) as z:
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

            FINAL_DIR.mkdir(parents=True, exist_ok=True)
            out_path = FINAL_DIR / "final_video.mp4"
            video.write_videofile(str(out_path), fps=30, codec="libx264", audio_codec="aac")
            st.session_state["video_path"] = str(out_path)

            with open(out_path, "rb") as f:
                st.download_button("Download Video", f, file_name="final_video.mp4")
        except Exception as e:
            st.error(f"Failed to assemble video: {e}")
        finally:
            if "tmp_dir" in locals() and tmp_dir.exists():
                shutil.rmtree(tmp_dir)
