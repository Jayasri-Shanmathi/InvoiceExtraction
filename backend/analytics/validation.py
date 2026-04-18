"""
Invoice Validation Module
Checks field presence, formats, and business rules.
Also computes a confidence score (0.0 - 1.0) per invoice.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ── Field-level helpers ────────────────────────────────────────────────────────

def _is_valid_date(value) -> bool:
    if not value:
        return False
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)))


def _is_positive_number(value) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


# ── Main validation function ───────────────────────────────────────────────────

def validate_invoice(invoice: dict) -> dict:
    """
    Validates an extracted invoice dict.

    Returns:
        {
            "status": "valid" | "faulty",
            "issues": ["list of issue strings"]
        }
    """
    issues = []

    vendor = invoice.get("vendor") or {}
    header = invoice.get("invoice_header") or {}
    items  = invoice.get("items") or []

    # Vendor checks
    if not vendor.get("name"):
        issues.append("Missing vendor name")
    if not vendor.get("gst_no"):
        issues.append("Missing vendor GST number")

    # Header checks
    if not header.get("invoice_number"):
        issues.append("Missing invoice number")

    if not _is_valid_date(header.get("invoice_date")):
        issues.append("Invalid or missing invoice date (expected YYYY-MM-DD)")

    amount = header.get("invoice_amount")
    if amount is None:
        issues.append("Missing invoice amount")
    elif not _is_positive_number(amount):
        issues.append(f"Invoice amount must be > 0, got: {amount}")

    # Items checks
    if not items:
        issues.append("No line items found")
    else:
        for i, item in enumerate(items):
            if not _is_positive_number(item.get("rate")):
                issues.append(f"Item {i+1}: invalid or missing rate")
            if not _is_positive_number(item.get("billed_qty")):
                issues.append(f"Item {i+1}: invalid or missing billed_qty")

    status = "faulty" if issues else "valid"
    logger.info("Validation result: %s | issues: %s", status, issues)

    return {"status": status, "issues": issues}


# ── Confidence scoring ─────────────────────────────────────────────────────────

def compute_confidence(invoice: dict, validation_result: dict) -> float:
    """
    Computes a confidence score (0.0 – 1.0) based on:
    - Field completeness
    - Format correctness (via validation issues)
    - Item-level data quality
    """
    score = 1.0
    penalty_per_issue = 0.08

    # Penalise for each validation issue
    score -= len(validation_result.get("issues", [])) * penalty_per_issue

    vendor = invoice.get("vendor") or {}
    header = invoice.get("invoice_header") or {}

    # Optional but valuable fields
    optional_fields = [
        vendor.get("email"),
        vendor.get("contact"),
        header.get("due_date"),
        header.get("irn"),
    ]
    missing_optional = sum(1 for f in optional_fields if not f)
    score -= missing_optional * 0.02

    # Item tax completeness
    items = invoice.get("items") or []
    if items:
        tax_filled = sum(
            1 for item in items
            if item.get("cgst_amount") or item.get("igst_amount")
        )
        tax_ratio = tax_filled / len(items)
        score -= (1 - tax_ratio) * 0.05

    return round(max(0.0, min(1.0, score)), 2)
