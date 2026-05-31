import io
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from legasafe_engine import process_pdf

app = FastAPI(
    title="Legasafe API",
    description="API to process bank statement PDFs for subscription and transaction data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Legasafe API is running"}

@app.post("/api/v1/process-pdf")
async def process_pdf_api(file: UploadFile = File(...), password: Optional[str] = Form(None)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB.")

    try:
        data = process_pdf(file_bytes, password=password)
        if data is None:
            raise HTTPException(status_code=400, detail="Failed to process PDF or no transactions found.")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
