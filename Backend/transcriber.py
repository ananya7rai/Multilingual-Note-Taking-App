from faster_whisper import WhisperModel
from pydub import AudioSegment
import os

model = WhisperModel("large-v3", device="cpu", compute_type="int8")

diarization_pipeline = None

def split_audio(file_path, max_length=30):
    try:
        audio = AudioSegment.from_mp3(file_path)
        length_ms = len(audio)
        chunks = []

        for i in range(0, length_ms, max_length * 1000):
            chunk = audio[i:i + max_length * 1000]
            chunk_path = f"{file_path}_chunk_{i // 1000}.mp3"
            chunk.export(chunk_path, format="mp3")
            chunks.append(chunk_path)

        return chunks
    except Exception as e:
        print(f"[ERROR] Failed to split audio: {e}")
        raise

def transcribe_audio(audio_path, max_length=30):
    print(f"[INFO] Transcribing: {audio_path}")
    chunks = split_audio(audio_path, max_length)
    full_transcription = ""

    for chunk in chunks:
        try:
            print(f"[INFO] Transcribing chunk: {chunk}")
            segments, _ = model.transcribe(chunk, beam_size=5)
            for segment in segments:
                full_transcription += segment.text.strip() + " "
        except Exception as e:
            print(f"[ERROR] Failed to transcribe chunk {chunk}: {e}")
        finally:
            if os.path.exists(chunk):
                os.remove(chunk)

    return full_transcription.strip()

def diarize_audio(audio_path):
    print(f"[INFO] Diarization skipped — pipeline not available.")
    return []

def diarized_transcript(audio_path):
    print("[INFO] Generating diarized transcript...")
    try:
        diarized = diarize_audio(audio_path)
        transcription = transcribe_audio(audio_path)

        if not diarized:
            return f"Transcription (no diarization available):\n{transcription}"

        speaker_lines = [
            f"{segment['speaker']} [{segment['start']:.1f}s - {segment['end']:.1f}s]"
            for segment in diarized
        ]

        return "\n".join(speaker_lines) + "\n\nTranscription:\n" + transcription
    except Exception as e:
        print(f"[ERROR] Failed to generate diarized transcript: {e}")
        return None
