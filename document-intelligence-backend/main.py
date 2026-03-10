from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pdfminer.high_level import extract_text
from utils.classifier import classify_document
from utils.extractor import extract_document_data
from utils.summarizer import generate_fallback_summary
from database import engine, SessionLocal
from models import Base, Document
import os
import shutil
import json

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Document Intelligence Backend is running"}


@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    db = SessionLocal()

    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"Received file: {file.filename}")
        print(f"Saved at: {file_path}")

        extracted_text = extract_text(file_path)

        document_type = classify_document(extracted_text)
        structured_data = extract_document_data(document_type, extracted_text)

        if not extracted_text or not extracted_text.strip():
            structured_data = {}
            extracted_text = ""

        summary_payload = generate_fallback_summary(
            document_type=document_type,
            text=extracted_text,
            structured_data=structured_data
        )

        new_document = Document(
            filename=file.filename,
            document_type=document_type,
            structured_data=json.dumps(structured_data),
            extracted_text=extracted_text,
            summary=summary_payload["summary"],
            key_points=json.dumps(summary_payload["key_points"]),
            recommended_next_action=summary_payload["recommended_next_action"]
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        return {
            "id": new_document.id,
            "filename": file.filename,
            "document_type": document_type,
            "message": "PDF uploaded, processed, summarized, and saved successfully",
            "structured_data": structured_data,
            "summary": summary_payload["summary"],
            "key_points": summary_payload["key_points"],
            "recommended_next_action": summary_payload["recommended_next_action"],
            "extracted_text": extracted_text[:3000]
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    finally:
        db.close()


@app.get("/documents")
def get_all_documents():
    db = SessionLocal()

    try:
        documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()

        results = []
        for doc in documents:
            results.append({
                "id": doc.id,
                "filename": doc.filename,
                "document_type": doc.document_type,
                "structured_data": json.loads(doc.structured_data) if doc.structured_data else {},
                "summary": doc.summary,
                "key_points": json.loads(doc.key_points) if doc.key_points else [],
                "recommended_next_action": doc.recommended_next_action,
                "uploaded_at": doc.uploaded_at,
            })

        return {"documents": results}

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    finally:
        db.close()