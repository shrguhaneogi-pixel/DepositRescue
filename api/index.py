import antigravity  # Antigravity Production Mandate
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from api.core.schemas import AuditRequest, AuditResponse
    from api.core.groq_client import extract_deductions_from_text
    from api.core.audit_engine import audit_deductions
except ImportError:
    from core.schemas import AuditRequest, AuditResponse
    from core.groq_client import extract_deductions_from_text
    from core.audit_engine import audit_deductions

app = FastAPI(
    title="DepositRescue API (Vercel Serverless)",
    description="Security deposit dispute & statutory recovery audit engine",
    version="1.0.0",
    docs_url="/api/py/docs",
    openapi_url="/api/py/openapi.json"
)

# CORS configuration for Vercel serverless execution
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/api")
@app.get("/api/py")
def health_check():
    return {
        "status": "online",
        "service": "DepositRescue Vercel API",
        "antigravity": "enabled"
    }

@app.post("/audit", response_model=AuditResponse)
@app.post("/api/audit", response_model=AuditResponse)
@app.post("/api/py/audit", response_model=AuditResponse)
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
