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
    return name.strip(" -:*•=\t\n")

def fallback_regex_extractor(text: str) -> ExtractedLLMResponse:
    """
    Fallback deterministic regex parser when GROQ_API_KEY is not set or API fails.
    Extracts dollar amounts (including commas) and line item descriptions from landlord text.
    """
    items = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines:
        # Match dollar or USD currency amounts first
        m = re.search(r"(?:\$|USD\s*)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)", line, re.IGNORECASE)
        if not m:
            # Fallback to colon or dash followed by numeric cost at line end
            m = re.search(r"[:\-\=]\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)\s*$", line)

        if m:
            cost_str = m.group(1).replace(",", "")
            try:
                cost = float(cost_str)
                if cost > 0:
                    start, end = m.span()
                    prefix = line[:start]
                    suffix = line[end:]
                    raw_name = prefix if prefix.strip() else suffix
                    name = clean_item_name(raw_name)
                    if not name:
                        name = "Landlord Deduction Item"
                    items.append(RawDeductionItem(item_name=name, cost=cost, category="Extracted Charge"))
                    continue
            except ValueError:
                pass

    if not items:
        items.append(RawDeductionItem(item_name="Unspecified Landlord Deduction", cost=250.0, category="General"))

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
        system_instruction = (
            "You are an expert security deposit audit assistant. "
            "Extract all itemized deductions from the landlord statement into valid JSON. "
            "Return JSON matching key 'deductions', where each item has 'item_name' (string), "
            "'cost' (number), 'category' (string), and 'explanation' (string)."
        )
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": f"Landlord Statement:\n{text}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=15.0,
        )
        
        content = response.choices[0].message.content
        if content:
            content = content.strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\n?", "", content)
                content = re.sub(r"\n?```$", "", content).strip()
            parsed = json.loads(content)
            
            # Normalize list vs dict payload format
            if isinstance(parsed, list):
                parsed = {"deductions": parsed}
            elif isinstance(parsed, dict) and "deductions" not in parsed and "items" in parsed:
                parsed["deductions"] = parsed.pop("items")

            return ExtractedLLMResponse.model_validate(parsed)
            
    except Exception as err:
        logger.warning(f"Groq API call warning: {err}. Using fallback parser.")
        
    return fallback_regex_extractor(text)
