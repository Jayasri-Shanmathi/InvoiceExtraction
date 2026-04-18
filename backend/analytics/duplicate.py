"""
Duplicate Invoice Detection
Compares vendor name, invoice amount, and invoice date.
Uses fuzzy matching for vendor names to catch near-duplicates.
"""

import logging
from typing import List, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

FUZZY_THRESHOLD = 0.85  # vendor name similarity threshold (0–1)


def _fuzzy_match(a: str, b: str) -> float:
    """Returns similarity ratio between two strings (0.0 – 1.0)."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def check_duplicate(invoice: dict, existing_invoices: List[dict]) -> dict:
    """
    Checks if an invoice is a duplicate of any existing invoice.

    Args:
        invoice: The new invoice dict (with vendor, invoice_header keys).
        existing_invoices: List of dicts from DB with keys:
                           vendor_name, invoice_amount, invoice_date, invoice_number

    Returns:
        {
            "is_duplicate": bool,
            "matched_invoice_number": str | None,
            "reason": str
        }
    """
    new_vendor  = (invoice.get("vendor") or {}).get("name", "") or ""
    new_amount  = _safe_float((invoice.get("invoice_header") or {}).get("invoice_amount"))
    new_date    = str((invoice.get("invoice_header") or {}).get("invoice_date") or "")
    new_inv_num = str((invoice.get("invoice_header") or {}).get("invoice_number") or "")

    for existing in existing_invoices:
        ex_vendor  = str(existing.get("vendor_name") or "")
        ex_amount  = _safe_float(existing.get("invoice_amount"))
        ex_date    = str(existing.get("invoice_date") or "")
        ex_inv_num = str(existing.get("invoice_number") or "")

        # Exact invoice number match → definite duplicate
        if new_inv_num and new_inv_num == ex_inv_num:
            return {
                "is_duplicate": True,
                "matched_invoice_number": ex_inv_num,
                "reason": "exact invoice number match",
            }

        # Fuzzy vendor + same amount + same date
        vendor_similarity = _fuzzy_match(new_vendor, ex_vendor)
        amount_match = (new_amount is not None and ex_amount is not None
                        and abs(new_amount - ex_amount) < 0.01)
        date_match = new_date and new_date == ex_date

        if vendor_similarity >= FUZZY_THRESHOLD and amount_match and date_match:
            return {
                "is_duplicate": True,
                "matched_invoice_number": ex_inv_num,
                "reason": f"fuzzy vendor match ({vendor_similarity:.0%}), same amount and date",
            }

    return {"is_duplicate": False, "matched_invoice_number": None, "reason": "no duplicate found"}


def _safe_float(val) -> Optional[float]:
    try:
        return float(str(val).replace(",", ""))
    except (TypeError, ValueError):
        return None
