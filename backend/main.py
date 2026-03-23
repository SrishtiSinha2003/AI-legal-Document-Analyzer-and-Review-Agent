from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import tempfile
import os

from dotenv import load_dotenv
import os

load_dotenv()

from pipeline.ingestion import ingest_pdf
from pipeline.ner import extract_entities
from pipeline.classifier import classify_clauses, score_risk
from agent.legal_agent import LegalAgent

app = FastAPI(title="AI Legal Document Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = LegalAgent()


@app.post("/api/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Step 1: Ingest PDF → segmented sections
        segments = ingest_pdf(tmp_path)

        # Step 2: NER on each segment
        enriched = []
        for seg in segments:
            entities = extract_entities(seg["text"])
            seg["entities"] = entities
            enriched.append(seg)

        # Step 3: Classify clauses + risk scoring
        classified = classify_clauses(enriched)

        # Step 4: Agent summary
        summary = agent.summarize(classified)

        return JSONResponse({
            "filename": file.filename,
            "segments": classified,
            "summary": summary,
            "total_clauses": len(classified),
            "risk_counts": {
                "high": sum(1 for s in classified if s["risk"] == "high"),
                "medium": sum(1 for s in classified if s["risk"] == "medium"),
                "low": sum(1 for s in classified if s["risk"] == "low"),
            }
        })
    finally:
        os.unlink(tmp_path)


@app.post("/api/chat")
async def chat_with_agent(payload: dict):
    question = payload.get("question", "")
    context = payload.get("context", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    answer = agent.chat(question, context)
    return {"answer": answer}


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
