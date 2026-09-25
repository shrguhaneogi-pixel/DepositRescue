import os
import re
import json
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

try:
    from api.core.schemas import ExtractedLLMResponse, RawDeductionItem
except ImportError:
    from core.schemas import ExtractedLLMResponse, RawDeductionItem

load_dotenv()

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def fallback_regex_extractor(text: str) -> ExtractedLLMResponse:
    """
    Fallback deterministic regex parser when GROQ_API_KEY is not set or API fails.
    Extracts dollar amounts and line item descriptions from landlord text.
    """
    items = []
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines:
        matched = False
        m1 = re.search(r"([A-Za-z0-9\s\/\-\'\(\)]+?)\s*(?:[:\-\=]\s*|\s+)\$([0-9]+(?:\.[0-9]{2})?)", line)
        if m1:
            name = m1.group(1).strip(" -:*•")
            cost = float(m1.group(2))
            if name and cost > 0:
                items.append(RawDeductionItem(item_name=name, cost=cost, category="Extracted Charge"))
                matched = True
                continue
                
        m2 = re.search(r"\$([0-9]+(?:\.[0-9]{2})?)\s*(?:[:\-\=]\s*|\s+)([A-Za-z0-9\s\/\-\'\(\)]+)", line)
        if m2 and not matched:
            cost = float(m2.group(1))
            name = m2.group(2).strip(" -:*•")
            if name and cost > 0:
                items.append(RawDeductionItem(item_name=name, cost=cost, category="Extracted Charge"))

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
        client = Groq(api_key=api_key)
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
            return ExtractedLLMResponse.model_validate(parsed)
            
    except Exception as err:
        print(f"Groq API call warning: {err}. Using fallback parser.")
        
    return fallback_regex_extractor(text)
