"""
Vendor Behavior Analysis
Detects if a new invoice is significantly higher than the vendor's historical average.
"""

import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

VENDOR_SPIKE_THRESHOLD = 2.0  # flag if amount > mean + N * std


def analyze_vendor_spend(
    vendor_name: str,
    new_amount: float,
    historical_amounts: List[float],
) -> dict:
    """
    Compares a new invoice amount against the vendor's historical spend.

    Args:
        vendor_name: Name of the vendor.
        new_amount: Amount on the new invoice.
        historical_amounts: Past invoice amounts for this vendor.

    Returns:
        {
            "vendor_anomaly": bool,
            "vendor_avg": float,
            "reason": str
        }
    """
    if not historical_amounts:
        return {
            "vendor_anomaly": False,
            "vendor_avg": None,
            "reason": "no historical data for this vendor",
        }

    arr  = np.array(historical_amounts, dtype=float)
    mean = float(np.mean(arr))
    std  = float(np.std(arr))

    threshold = mean + VENDOR_SPIKE_THRESHOLD * std if std > 0 else mean * 1.5

    is_anomaly = new_amount > threshold

    reason = (
        f"amount {new_amount:.2f} exceeds vendor avg {mean:.2f} by more than {VENDOR_SPIKE_THRESHOLD}σ"
        if is_anomaly
        else f"within normal range for vendor (avg={mean:.2f})"
    )

    logger.info("Vendor analysis [%s]: anomaly=%s | %s", vendor_name, is_anomaly, reason)

    return {
        "vendor_anomaly": is_anomaly,
        "vendor_avg": round(mean, 2),
        "reason": reason,
    }
