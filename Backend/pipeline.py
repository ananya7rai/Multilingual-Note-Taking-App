from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fpdf import FPDF
from pathlib import Path
from pydantic import BaseModel
import shutil
import sqlite3
import os

from transcriber import transcribe_audio
from summarizer import summarize_text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_files"
STATIC_DIR = "static"
Path(UPLOAD_DIR).mkdir(exist_ok=True)
Path(STATIC_DIR).mkdir(exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect("meetings.db")
    conn.row_factory = sqlite3.Row
    return conn

def insert_meeting(transcript, summary, action_items="", decisions=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meetings (transcript, summary, action_items, decisions) 
        VALUES (?, ?, ?, ?)
    """, (transcript, summary, action_items, decisions))
    conn.commit()
    meeting_id = cursor.lastrowid
    conn.close()
    return meeting_id

@app.post("/process_meeting")
async def process_meeting(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        transcript = transcribe_audio(file_path)
        summary_text = summarize_text(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        os.remove(file_path)

    action_items = "[Not available — needs NLP tagging]"
    decisions = "[Not available — needs deeper parsing]"

    meeting_id = insert_meeting(transcript, summary_text, action_items, decisions)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Meeting Summary", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, summary_text)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Transcript:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, transcript)

    pdf_output_path = Path(STATIC_DIR) / f"meeting_{meeting_id}_summary.pdf"
    pdf.output(str(pdf_output_path))

    return {
        "meeting_id": meeting_id,
        "transcript": transcript,
        "summary": summary_text,
        "pdf_link": f"/static/meeting_{meeting_id}_summary.pdf"
    }

@app.get("/export/{meeting_id}")
async def export_pdf(meeting_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Meeting not found")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Meeting Summary", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['summary'])

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Action Items:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['action_items'])

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Decisions:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['decisions'])

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Transcript:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['transcript'])

    pdf_output_path = Path(STATIC_DIR) / f"meeting_{meeting_id}_summary.pdf"
    pdf.output(str(pdf_output_path))

    return {
        "message": "PDF generated successfully!",
        "pdf_link": f"/static/meeting_{meeting_id}_summary.pdf"
    }

class SearchQuery(BaseModel):
    query: str

@app.post("/search")
async def search_meetings(payload: SearchQuery):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, summary FROM meetings WHERE transcript LIKE ?", ('%' + payload.query + '%',))
    results = cursor.fetchall()
    conn.close()

    return {
        "results": [{"id": row["id"], "summary": row["summary"]} for row in results]
    }
