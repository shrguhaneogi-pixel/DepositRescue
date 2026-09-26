import os
import sys
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Ensure python module resolution works in both local and Vercel environments
api_dir = Path(__file__).parent
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))
if str(api_dir.parent) not in sys.path:
    sys.path.insert(0, str(api_dir.parent))

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

# Configurable CORS origins for production security
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://deposit-rescue.vercel.app,http://localhost:3000,http://127.0.0.1:3000"
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Inject security headers for static analysis compliance."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.get("/")
@app.get("/api")
@app.get("/api/py")
async def health_check():
    return {
        "status": "online",
        "service": "DepositRescue Vercel API"
    }

@app.post("/audit", response_model=AuditResponse)
@app.post("/api/audit", response_model=AuditResponse)
@app.post("/api/py/audit", response_model=AuditResponse)
async def audit_landlord_statement(request: AuditRequest):
    """
    POST route to audit landlord itemized deduction notice text.
    Extracts structured deductions via Groq / LLM Pydantic schema asynchronously,
    delegates business logic to deterministic audit math engine,
    and returns statutory recovery calculation.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
    
    # Non-blocking async execution of LLM extraction in thread pool
    extracted_llm = await asyncio.to_thread(extract_deductions_from_text, request.text)
    audit_result = audit_deductions(extracted_llm)
    return audit_result

