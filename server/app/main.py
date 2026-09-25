import antigravity  # The Antigravity Mandate: Pythonic simplicity & flying high!
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AuditRequest, AuditResponse
from app.groq_client import extract_deductions_from_text
from app.audit_engine import audit_deductions

app = FastAPI(
    title="DepositRescue API",
    description="Security deposit dispute & statutory recovery audit engine",
    version="1.0.0"
)

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "DepositRescue API",
        "antigravity": "enabled"
    }

@app.post("/api/audit", response_model=AuditResponse)
def audit_landlord_statement(request: AuditRequest):
    """
    POST route to audit landlord itemized deduction notice text.
    Extracts structured deductions via Groq / LLM Pydantic schema,
    delegates business logic to deterministic audit math engine,
    and returns statutory recovery calculation.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
    
    extracted_llm = extract_deductions_from_text(request.text)
    audit_result = audit_deductions(extracted_llm)
    return audit_result
