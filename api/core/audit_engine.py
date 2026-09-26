import json
from pathlib import Path
from typing import List, Tuple

try:
    from api.core.schemas import RawDeductionItem, AuditedDeductionItem, AuditResponse, ExtractedLLMResponse
except ImportError:
    from core.schemas import RawDeductionItem, AuditedDeductionItem, AuditResponse, ExtractedLLMResponse

RULES_FILE = Path(__file__).parent / "rules.json"

def load_rules() -> Tuple[List[str], float]:
    if RULES_FILE.exists():
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("routine_maintenance_flags", []), data.get("statutory_multiplier", 2.0)
    return ["painting", "cleaning", "wear and tear", "nail holes"], 2.0

def audit_deductions(extracted: ExtractedLLMResponse) -> AuditResponse:
    """
    Deterministic mathematical engine to audit extracted landlord deductions against statutory tenant rights rules.
    Zeroes out illegal charges for routine wear and tear, and calculates statutory recovery amount.
    """
    flags, multiplier = load_rules()
    audited_items: List[AuditedDeductionItem] = []
    
    raw_total = 0.0
    illegal_total = 0.0

    for raw in extracted.deductions:
        cost = round(max(0.0, float(raw.cost)), 2)
        raw_total += cost
        
        name_lower = raw.item_name.lower()
        explanation_lower = (raw.explanation or "").lower()
        category_lower = (raw.category or "").lower()
        
        matched_flag = None
        for flag in flags:
            if flag in name_lower or flag in explanation_lower or flag in category_lower:
                matched_flag = flag
                break
        
        is_routine = matched_flag is not None
        
        if is_routine:
            adjusted_cost = 0.0
            is_illegal = True
            illegal_total += cost
            exp = (
                f"Flagged as routine maintenance ('{matched_flag}'). "
                f"Under tenant protection law, landlords cannot deduct for normal wear and tear."
            )
        else:
            adjusted_cost = cost
            is_illegal = False
            exp = raw.explanation or "Valid tenant-caused damage repair charge."
            
        audited_items.append(
            AuditedDeductionItem(
                item_name=raw.item_name,
                original_cost=cost,
                adjusted_cost=adjusted_cost,
                is_routine_maintenance=is_routine,
                is_illegal=is_illegal,
                category=raw.category or "General",
                matched_flag=matched_flag,
                explanation=exp,
            )
        )

    raw_total = round(raw_total, 2)
    illegal_total = round(illegal_total, 2)
    allowed_total = round(raw_total - illegal_total, 2)
    statutory_recovery = round(illegal_total * multiplier, 2)
    
    mult_str = f"{int(multiplier)}x" if float(multiplier).is_integer() else f"{multiplier}x"
    summary = (
        f"Audited {len(audited_items)} itemized charge(s). "
        f"Found ${illegal_total:.2f} in unlawful routine maintenance charges. "
        f"Statutory dispute recovery estimate: ${statutory_recovery:.2f} ({mult_str} illegal withholdings)."
    )

    return AuditResponse(
        raw_total=raw_total,
        illegal_total=illegal_total,
        allowed_total=allowed_total,
        statutory_recovery=statutory_recovery,
        statutory_multiplier=multiplier,
        items=audited_items,
        summary=summary,
    )
