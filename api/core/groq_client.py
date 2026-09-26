import os
import re
import json
import logging
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

try:
    from api.core.schemas import ExtractedLLMResponse, RawDeductionItem
except ImportError:
    from core.schemas import ExtractedLLMResponse, RawDeductionItem

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def clean_item_name(name: str) -> str:
    """Strips leading list numbers, bullets, and surrounding whitespace/punctuation."""
    name = re.sub(r"^(?:[0-9]+[\.\)]\s*|[\-\*•\>]\s*)", "", name.strip())
    name = re.sub(r"\s+(?:USD|\$)?\s*[0-9,]+(?:\.[0-9]{1,2})?$", "", name, flags=re.IGNORECASE)
    return name.strip(" -:*•=\t\n")

def fallback_regex_extractor(text: str) -> ExtractedLLMResponse:
    """
    Fallback deterministic regex parser when GROQ_API_KEY is not set or API fails.
    Extracts dollar amounts and line item descriptions from landlord text.
    """
    items = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines:
        # Pattern 1: Description followed by $ or USD and amount (e.g. "Wall repainting: $1,200.00" or "Interior paint USD 250.00")
        m1 = re.search(r"([A-Za-z0-9\s\/\-\'\(\)]+?)\s*(?:[:\-\=]\s*|\s+)(?:USD\s*|\$)\s*([0-9,]+(?:\.[0-9]{1,2})?)", line, re.IGNORECASE)
        if m1:
            name = clean_item_name(m1.group(1))
            try:
                cost = float(m1.group(2).replace(",", ""))
                if name and cost > 0:
                    items.append(RawDeductionItem(item_name=name, cost=cost, category="Extracted Charge"))
                    continue
            except ValueError:
                pass

        # Pattern 2: Amount preceding description (e.g. "$150.00 for carpet cleaning")
        m2 = re.search(r"(?:USD\s*|\$)\s*([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:[:\-\=]\s*|\s+(?:for|on)?\s*)([A-Za-z0-9\s\/\-\'\(\)]+)", line, re.IGNORECASE)
        if m2:
            try:
                cost = float(m2.group(1).replace(",", ""))
                name = clean_item_name(m2.group(2))
                if name and cost > 0:
                    items.append(RawDeductionItem(item_name=name, cost=cost, category="Extracted Charge"))
            except ValueError:
                pass

    if not items:
        return ExtractedLLMResponse(
            deductions=[],
            landlord_statement_summary="No monetary landlord deductions identified in input."
        )

    return ExtractedLLMResponse(
        deductions=items,
        landlord_statement_summary="Extracted via deterministic fallback parser."
    )

def extract_deductions_from_text(text: str) -> ExtractedLLMResponse:
    """
    Extracts itemized deductions from raw landlord text using Groq API with Pydantic v2 schema.
    Falls back gracefully if Groq API key is unconfigured or fails.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return fallback_regex_extractor(text)

    try:
        client = Groq(api_key=api_key, timeout=15.0)
        prompt = (
            "You are an expert security deposit audit assistant. "
            "Extract all itemized deductions from the landlord statement into valid JSON. "
            "Return JSON matching key 'deductions', where each item has 'item_name' (string), "
            "'cost' (number), 'category' (string), and 'explanation' (string).\n\n"
            f"Landlord Text:\n{text}"
        )
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You output strictly valid JSON conforming to the requested schema."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        if content:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "deductions" in parsed:
                return ExtractedLLMResponse.model_validate(parsed)
            elif isinstance(parsed, list):
                return ExtractedLLMResponse(deductions=[RawDeductionItem.model_validate(i) for i in parsed])
            
    except Exception as err:
        logger.warning(f"Groq API call warning: {err}. Using fallback parser.")
        
    return fallback_regex_extractor(text)
