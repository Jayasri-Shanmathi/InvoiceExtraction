import json
import asyncio
from llm.gemini_client import model
from .invoice_prompt import INVOICE_EXTRACTION_PROMPT
import re

import json
import re

def _extract_invoice_sync(images: list, prompt: str) -> dict:
    response = model.generate_content(
        [prompt] + images,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    raw_text = response.text

    # 🔍 Extract JSON safely
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Gemini response")

    json_text = match.group(0)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON after cleanup: {e}")


def extract_invoice(images: list, prompt: str) -> dict:
    response = model.generate_content(
        [prompt] + images,
        generation_config={
            "temperature": 0,
            "response_mime_type": "application/json"
        }
    )

    try:
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError("Gemini returned invalid JSON")
