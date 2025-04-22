# Multilingual Note Taking App

This project is a full-stack AI-powered meeting transcription and summarization system that:

- Accepts audio uploads (in any supported language)
- Transcribes the audio using `faster-whisper`
- Optionally performs speaker diarization with `pyannote-audio`
- Summarizes the transcript using transformer-based summarization (T5/BART/etc.)
- Saves transcripts, summaries, decisions, and action items in a local SQLite database
- Allows downloading a structured PDF report of the meeting
- Enables keyword-based transcript search via the frontend

---

## 🚀 Features

✅ Audio transcription (Whisper Large v3)  
✅ Summarization using Transformer models  
✅ Speaker diarization support *(optional)*  
✅ PDF report generation  
✅ Search meetings by transcript content  
✅ Full frontend integration with React  
✅ Lightweight & local — no cloud APIs required  

---


---

## 🧠 How it Works

1. User uploads audio from the React frontend
2. Backend transcribes audio using `faster-whisper`
3. Transcript is summarized using a transformer model (e.g., `t5-small`)
4. Results are saved in `SQLite` and a PDF summary is generated
5. User can download the summary or search transcripts by keywords

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

bash
git clone (https://github.com/ananya7rai/Multilingual-Note-Taking-App)
cd multilingual-note-taking

Create Virtual Environment
conda create -n asr_env python=3.10
conda activate asr_env

Install Backend Dependencies
cd Multilingual-Note-Taking-App/Backend
pip install -r requirements.txt

brew install ffmpeg     # for macOS

Set Environment Variables
export HUGGINGFACE_TOKEN=your_hf_token_here

Run Backend (FastAPI + Flask)
cd multilingual-asr/Backend
uvicorn main:app --reload

Run Frontend (React)
cd multilingual-asr/frontend
npm install
npm start

Sample Usage
Upload an audio file
See transcript and summary appear on the frontend
Click "Download PDF" to generate a structured meeting report
Search for past meetings using keywords

📝 Tech Stack

Backend: FastAPI, Flask, Python, SQLite, PyAnnote, Faster-Whisper
NLP Models: Whisper v3, T5/BART/PEGASUS (via Hugging Face)
Frontend: React + Axios + Tailwind (optional)
PDF Generation: fpdf
Audio Processing: pydub, ffmpeg

🛠️ Future Improvements

Role-based action extraction from transcript
Upload multilingual PDFs
Real-time transcription
Cloud storage for large meetings

🤝 Credits
Developed by Shashwat Singh and Ananya Rai
Special thanks to the open-source communities of 🤗 HuggingFace, OpenAI Whisper, and PyAnnote Audio.

📄 License
This project is licensed under the MIT License.






