import re
from typing import Any


def _score_field(key: str, value: Any) -> float:
    """Rule-based confidence score (0.0 - 1.0) for a single field."""
    if value is None or value == "" or value == "null":
        return 0.0

    score = 1.0

    # Date format check
    if "date" in key:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)):
            score -= 0.4

    # GST number format (Indian): 15 alphanumeric chars
    if key == "gst_no":
        if not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", str(value)):
            score -= 0.3

    # Numeric fields must be positive
    if key in ("invoice_amount", "grand_total", "taxable_value", "rate", "billed_qty", "total_value"):
        try:
            if float(value) <= 0:
                score -= 0.5
        except (TypeError, ValueError):
            score -= 0.6

    # Invoice number shouldn't be empty or suspiciously short
    if key == "invoice_number":
        if len(str(value).strip()) < 2:
            score -= 0.4

    # Tax consistency: cgst_percent should equal sgst_percent (checked at item level externally)
    if key in ("cgst_amount", "sgst_amount", "igst_amount"):
        try:
            if float(value) < 0:
                score -= 0.5
        except (TypeError, ValueError):
            score -= 0.4

    return round(max(0.0, min(1.0, score)), 2)


def _score_section(section: dict) -> dict:
    return {key: _score_field(key, val) for key, val in section.items()}


def _score_items(items: list) -> list:
    scored = []
    for item in items:
        item_scores = _score_section(item)

        # Extra rule: cgst_percent must equal sgst_percent
        cgst = item.get("cgst_percent")
        sgst = item.get("sgst_percent")
        if cgst is not None and sgst is not None:
            try:
                if float(cgst) != float(sgst):
                    item_scores["cgst_percent"] = round(item_scores["cgst_percent"] - 0.3, 2)
                    item_scores["sgst_percent"] = round(item_scores["sgst_percent"] - 0.3, 2)
            except (TypeError, ValueError):
                pass

        scored.append(item_scores)
    return scored


def compute_confidence(invoice: dict) -> dict:
    """
    Returns a confidence dict mirroring the invoice structure.
    Each field value is replaced with a score between 0.0 and 1.0.
    """
    confidence = {}

    if "vendor" in invoice and isinstance(invoice["vendor"], dict):
        confidence["vendor"] = _score_section(invoice["vendor"])

    if "invoice_header" in invoice and isinstance(invoice["invoice_header"], dict):
        confidence["invoice_header"] = _score_section(invoice["invoice_header"])

    if "items" in invoice and isinstance(invoice["items"], list):
        confidence["items"] = _score_items(invoice["items"])

    if "summary" in invoice and isinstance(invoice["summary"], dict):
        confidence["summary"] = _score_section(invoice["summary"])

    return confidence
