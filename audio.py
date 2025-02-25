import yt_dlp
import whisper
import os

def download_audio(youtube_url, output_filename="audio.mp3"):
    """Downloads audio from a YouTube video using yt-dlp and ensures correct filename."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_filename[:-4],  # Remove .mp3 to avoid double extension
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    # Ensure the correct filename is used
    if not os.path.exists(output_filename) and os.path.exists(output_filename + ".mp3"):
        os.rename(output_filename + ".mp3", output_filename)

    return output_filename

def transcribe_audio(audio_path):
    """Transcribes audio using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def main():
    youtube_url = input("Enter YouTube video URL: ")
    audio_file = download_audio(youtube_url)

    print("Transcribing audio... This may take a while.")
    transcript = transcribe_audio(audio_file)

    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript)

    print("\n✅ Transcription complete! Saved as 'transcript.txt'.")

    os.remove(audio_file)  # Clean up

if __name__ == "__main__":
    main()
