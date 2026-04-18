import json
import re
import logging
from llm.gemini_client import model
from llm.invoice_prompt import INVOICE_EXTRACTION_PROMPT, INVOICE_EXTRACTION_PROMPT_STRICT

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

PROMPTS = [
    INVOICE_EXTRACTION_PROMPT,
    INVOICE_EXTRACTION_PROMPT_STRICT,
    INVOICE_EXTRACTION_PROMPT_STRICT,  # 3rd attempt: same strict prompt, different temp
]

TEMPERATURES = [0, 0, 0.1]


def _parse_response(raw_text: str) -> dict:
    """Layer 2: Extract and validate JSON from Gemini response."""
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Gemini response")

    data = json.loads(match.group(0))

    # Required top-level sections
    for section in ["vendor", "invoice_header", "items", "summary"]:
        if section not in data:
            raise ValueError(f"Missing required section: {section}")

    return data


def extract_invoice(images: list, prompt: str = INVOICE_EXTRACTION_PROMPT) -> dict:
    """
    3-layer protected extraction with retry logic.
    Layer 1: try/except per attempt
    Layer 2: JSON validation + required field check
    Layer 3: retry with stricter prompt on failure
    """
    last_error = None

    for attempt in range(MAX_RETRIES):
        current_prompt = PROMPTS[attempt]
        current_temp = TEMPERATURES[attempt]

        try:
            logger.info(f"Gemini extraction attempt {attempt + 1}/{MAX_RETRIES}")

            # Layer 1: basic try/catch
            response = model.generate_content(
                [current_prompt] + images,
                generation_config={
                    "temperature": current_temp,
                    "response_mime_type": "application/json"
                }
            )

            # Layer 2: JSON validation
            data = _parse_response(response.text)
            logger.info(f"Extraction succeeded on attempt {attempt + 1}")
            return data

        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed (JSON/validation): {e}")

        except Exception as e:
            last_error = e
            logger.error(f"Attempt {attempt + 1} failed (Gemini error): {e}")

    # Layer 3: all retries exhausted
    raise RuntimeError(f"Invoice extraction failed after {MAX_RETRIES} attempts. Last error: {last_error}")
