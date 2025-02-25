import streamlit as st
import yt_dlp
import whisper
import os

def download_audio(youtube_url, output_filename="audio.mp3"):
    """Downloads audio from a YouTube video using yt-dlp and ensures correct filename."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_filename[:-4],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "quiet": True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    if not os.path.exists(output_filename) and os.path.exists(output_filename + ".mp3"):
        os.rename(output_filename + ".mp3", output_filename)
    
    return output_filename

def transcribe_audio(audio_path):
    """Transcribes audio using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def main():
    st.title("YouTube Video to Transcript Converter")
    
    youtube_url = st.text_input("Enter YouTube Video URL")
    if st.button("Generate Transcript"):
        if youtube_url:
            with st.spinner("Downloading audio..."):
                audio_file = download_audio(youtube_url)
            
            with st.spinner("Transcribing audio... This may take a while."):
                transcript = transcribe_audio(audio_file)
                os.remove(audio_file) 
            
            st.subheader("Transcript:")
            st.text_area("", transcript, height=300)
            
            st.download_button("Download Transcript", transcript, file_name="transcript.txt")
        else:
            st.warning("Please enter a valid YouTube URL.")

if __name__ == "__main__":
    main()
