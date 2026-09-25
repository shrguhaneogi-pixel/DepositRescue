from typing import List, Optional
from pydantic import BaseModel, Field

class RawDeductionItem(BaseModel):
    item_name: str = Field(..., description="Name or description of the claimed landlord deduction item")
    cost: float = Field(..., description="Amount charged/withheld by the landlord for this item in USD")
    category: Optional[str] = Field("Uncategorized", description="Category such as Painting, Cleaning, Damage, Repairs")
    explanation: Optional[str] = Field(None, description="Brief justification or context provided in the notice")

class ExtractedLLMResponse(BaseModel):
    deductions: List[RawDeductionItem] = Field(default_factory=list, description="List of itemized deductions extracted from text")
    landlord_statement_summary: Optional[str] = Field(None, description="Short summary of the landlord's claim")

class AuditedDeductionItem(BaseModel):
    item_name: str
    original_cost: float
    adjusted_cost: float
    is_routine_maintenance: bool
    is_illegal: bool
    category: str
    matched_flag: Optional[str] = None
    explanation: str

class AuditRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Itemized landlord deduction notice or text statement")

class AuditResponse(BaseModel):
    raw_total: float
    illegal_total: float
    allowed_total: float
    statutory_recovery: float
    statutory_multiplier: float
    items: List[AuditedDeductionItem]
    summary: str
