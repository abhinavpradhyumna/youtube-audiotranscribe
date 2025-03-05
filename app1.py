import yt_dlp
import whisper
import os
import tempfile
import sys
from pathlib import Path
import time
from typing import Optional
import re
import streamlit as st

def clear_line():
    """Clears the current line in the terminal."""
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()

def print_status(message: str, done: bool = False):
    """Prints a status message with dynamic updating."""
    clear_line()
    sys.stdout.write(message)
    sys.stdout.flush()
    if done:
        sys.stdout.write('\n')
        sys.stdout.flush()

def download_audio(youtube_url: str, output_path: str) -> Optional[str]:
    """Downloads audio from YouTube with progress feedback."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path[:-4],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        'noplaylist': True,
        'retries': 3,
        'fragment_retries': 3,
        'nooverwrites': True,
        'continuedl': True,
    }
    
    try:
        st.write("Downloading audio...")
        start_time = time.time()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        possible_path = output_path[:-4] + '.mp3'
        if os.path.exists(possible_path) and not os.path.exists(output_path):
            os.rename(possible_path, output_path)
        
        if not os.path.exists(output_path):
            raise Exception("Audio file not found after download")
        
        elapsed = time.time() - start_time
        st.success(f"Audio downloaded successfully in {elapsed:.1f} seconds")
        return output_path
    
    except Exception as e:
        st.error(f"Error downloading audio: {str(e)}")
        return None

def transcribe_audio(audio_path: str) -> Optional[str]:
    """Transcribes audio with progress feedback."""
    try:
        st.write("Loading Whisper model...")
        model = whisper.load_model("small")
        
        st.write("Transcribing audio (this may take a while)...")
        start_time = time.time()
        
        result = model.transcribe(
            audio_path,
            fp16=False,
            language='en',
            verbose=False,
        )
        
        elapsed = time.time() - start_time
        st.success(f"Transcription completed in {elapsed:.1f} seconds")
        return result["text"]
    
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def get_valid_video_id(youtube_url: str) -> str:
    """Extracts a clean video ID from a YouTube URL."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard YouTube ID pattern
        r'youtu\.be\/([0-9A-Za-z_-]{11})'    # Shortened youtu.be pattern
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return "video"  # Fallback if no ID found

def save_transcript(transcript: str, youtube_url: str) -> Optional[str]:
    """Saves transcript with feedback using a clean filename."""
    try:
        video_id = get_valid_video_id(youtube_url)
        filename = f"transcript_{video_id}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        st.success(f"Transcript saved successfully to {filename}")
        return filename
    except Exception as e:
        st.error(f"Error saving transcript: {str(e)}")
        return None

def main():
    st.title("YouTube Video Transcriber")
    youtube_url = st.text_input("Enter YouTube Video URL")
    
    if st.button("Process Video"):
        if not youtube_url:
            st.error("Error: No URL provided")
            return
        
        st.write(f"Processing video: {youtube_url}")
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            audio_path = os.path.join(tmpdirname, "audio.mp3")
            
            audio_file = download_audio(youtube_url, audio_path)
            if not audio_file:
                return
            
            transcript = transcribe_audio(audio_file)
            if transcript is None:
                return
            
            saved_file = save_transcript(transcript, youtube_url)
            if saved_file:
                preview = transcript[:100] + "..." if len(transcript) > 100 else transcript
                st.subheader("Transcript Preview:")
                st.write(preview)
                st.write(f"Full transcript available in: {saved_file}")
                
                st.download_button(
                    label="Download Transcript",
                    data=transcript,
                    file_name=saved_file,
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
