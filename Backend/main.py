from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transcriber import transcribe_audio
from summarizer import summarize_text
from fpdf import FPDF
from pathlib import Path
import shutil
import sqlite3
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

Path("static").mkdir(parents=True, exist_ok=True)
Path("uploads").mkdir(parents=True, exist_ok=True)
Path("temp_files").mkdir(parents=True, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect("meetings.db")
    conn.row_factory = sqlite3.Row
    return conn

def insert_meeting(filename: str, transcript: str, summary: str, action_items: str = "", decisions: str = "") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO meetings (transcript, summary, action_items, decisions) VALUES (?, ?, ?, ?)",
        (transcript, summary, action_items, decisions)
    )
    conn.commit()
    meeting_id = cursor.lastrowid
    conn.close()
    return meeting_id

@app.post("/process_meeting")
async def process_meeting(file: UploadFile = File(...)):
    file_path = os.path.join("temp_files", f"temp_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        transcript = transcribe_audio(file_path)
        summary = summarize_text(transcript)
        os.remove(file_path)

        meeting_id = insert_meeting(file.filename, transcript, summary)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Meeting Summary", ln=True, align='C')
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Summary:\n{summary}")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "Action Items:\n")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "Decisions:\n")
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"Transcript:\n{transcript}")

        pdf_output_path = Path(f"static/meeting_{meeting_id}_summary.pdf")
        pdf.output(str(pdf_output_path))

        return JSONResponse(content={
            "meeting_id": meeting_id,
            "transcript": transcript,
            "summary": summary,
            "pdf_link": f"/static/meeting_{meeting_id}_summary.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

class MeetingTranscript(BaseModel):
    transcript: str

@app.post("/summarize")
async def summarize_meeting(data: MeetingTranscript):
    try:
        summary = summarize_text(data.transcript)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

class SearchBody(BaseModel):
    query: str

@app.post("/search")
async def search_meetings(body: SearchBody):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE transcript LIKE ?", ('%' + body.query + '%',))
    results = cursor.fetchall()
    conn.close()

    if results:
        return {"results": [dict(row) for row in results]}
    else:
        raise HTTPException(status_code=404, detail="No matching transcripts found")

@app.get("/export/{meeting_id}")
async def export_pdf(meeting_id: int):
    pdf_path = Path(f"static/meeting_{meeting_id}_summary.pdf")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path=pdf_path, filename=pdf_path.name, media_type='application/pdf')
