"""
Anomaly Detection Module
Supports two interchangeable methods:
  - "statistical": mean ± 2*std threshold
  - "isolation_forest": sklearn IsolationForest
Switch via ANOMALY_METHOD env var or pass method= to detect_anomaly().
"""

import os
import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

ANOMALY_METHOD = os.getenv("ANOMALY_METHOD", "statistical")  # or "isolation_forest"


# ── Statistical method ─────────────────────────────────────────────────────────

def _statistical_anomaly(amount: float, historical_amounts: List[float]) -> dict:
    """Flags invoice if amount deviates more than 2 std from the mean."""
    if len(historical_amounts) < 3:
        return {"is_anomaly": False, "reason": "insufficient historical data"}

    arr  = np.array(historical_amounts, dtype=float)
    mean = float(np.mean(arr))
    std  = float(np.std(arr))

    if std == 0:
        return {"is_anomaly": False, "reason": "no variance in historical data"}

    z_score = abs(amount - mean) / std
    is_anomaly = z_score > 2.0

    return {
        "is_anomaly": is_anomaly,
        "reason": f"z-score {z_score:.2f} (mean={mean:.2f}, std={std:.2f})" if is_anomaly else "within normal range",
    }


# ── Isolation Forest method ────────────────────────────────────────────────────

def _isolation_forest_anomaly(amount: float, historical_amounts: List[float]) -> dict:
    """Uses sklearn IsolationForest trained on historical amounts."""
    try:
        from sklearn.ensemble import IsolationForest
    except ImportError:
        logger.warning("scikit-learn not installed, falling back to statistical method")
        return _statistical_anomaly(amount, historical_amounts)

    if len(historical_amounts) < 5:
        return {"is_anomaly": False, "reason": "insufficient data for isolation forest"}

    X = np.array(historical_amounts + [amount]).reshape(-1, 1)
    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(X[:-1])  # train on historical only

    prediction = clf.predict([[amount]])[0]  # -1 = anomaly, 1 = normal
    is_anomaly = prediction == -1

    return {
        "is_anomaly": is_anomaly,
        "reason": "isolation forest flagged as outlier" if is_anomaly else "within normal range",
    }


# ── Public interface ───────────────────────────────────────────────────────────

def detect_anomaly(
    amount: float,
    historical_amounts: List[float],
    method: Optional[str] = None,
) -> dict:
    """
    Detects whether an invoice amount is anomalous.

    Args:
        amount: The invoice amount to check.
        historical_amounts: List of past invoice amounts (same vendor or global).
        method: "statistical" | "isolation_forest" (defaults to ANOMALY_METHOD env var).

    Returns:
        { "is_anomaly": bool, "reason": str }
    """
    chosen = method or ANOMALY_METHOD

    try:
        if chosen == "isolation_forest":
            return _isolation_forest_anomaly(amount, historical_amounts)
        return _statistical_anomaly(amount, historical_amounts)
    except Exception as e:
        logger.error("Anomaly detection failed: %s", e)
        return {"is_anomaly": False, "reason": f"detection error: {str(e)}"}
