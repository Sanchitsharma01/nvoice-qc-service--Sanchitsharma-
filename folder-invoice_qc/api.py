import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .validator import run_batch_validation
from .extractor import extract_invoice_from_pdf

app = FastAPI(title="Invoice QC Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/validate-json")
def validate_json_endpoint(payload: List[Dict[str, Any]]):
    if not payload:
        raise HTTPException(status_code=400, detail="Payload empty")
    return run_batch_validation(payload)

@app.post("/extract-and-validate-pdfs")
async def extract_and_validate_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    extracted_data = []
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                continue
            file_loc = temp_path / file.filename
            with open(file_loc, "wb+") as file_obj:
                shutil.copyfileobj(file.file, file_obj)
            
            try:
                data = extract_invoice_from_pdf(str(file_loc))
                if data:
                    data["_source_file"] = file.filename
                    extracted_data.append(data)
            except Exception:
                pass

    return {
        "validation_report": run_batch_validation(extracted_data),
        "extracted_data": extracted_data
    }
