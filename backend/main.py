import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
from preprocessing import preprocess_image
from llm.extraction import extract_invoice
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.DB.connections import get_db
from infrastructure.DB.invoice_repository import (
    save_invoice_data,
    normalize_invoice_data,
    get_all_invoice_amounts,
    get_vendor_invoice_amounts,
    get_existing_invoices_for_duplicate_check,
    get_analytics_summary,
    get_alerts,
)
from fastapi.middleware.cors import CORSMiddleware

# Analytics modules
from analytics.validation import validate_invoice, compute_confidence
from analytics.anomaly import detect_anomaly
from analytics.duplicate import check_duplicate
from analytics.vendor_analysis import analyze_vendor_spend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Upload & Extract ───────────────────────────────────────────────────────────

@app.post("/Upload-file/")
async def create_upload_file(file: UploadFile = File(...)):
    logger.info("Upload started: %s", file.filename)
    contents = await file.read()

    processed_images = []
    try:
        if file.content_type == "application/pdf":
            images = convert_from_bytes(contents)
        else:
            images = [Image.open(BytesIO(contents))]

        for img in images:
            processed_images.append(preprocess_image(img))

        gemini_output = extract_invoice(processed_images)

        # Run validation + confidence on extracted data (no DB needed here)
        validation = validate_invoice(gemini_output)
        confidence = compute_confidence(gemini_output, validation)

        return {
            "data": gemini_output,
            "validation": validation,
            "confidence_score": confidence,
        }

    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Save Invoice (with full analytics pipeline) ────────────────────────────────

@app.post("/save-invoice/")
async def save_invoice(invoice_data: dict, db: AsyncSession = Depends(get_db)):
    invoice_data = normalize_invoice_data(invoice_data)
    if not invoice_data:
        raise HTTPException(status_code=400, detail="No invoice data provided")

    try:
        # 1. Validation
        validation = validate_invoice(invoice_data)
        confidence = compute_confidence(invoice_data, validation)

        # 2. Anomaly detection (global)
        amount = float(invoice_data.get("invoice_header", {}).get("invoice_amount") or 0)
        historical = await get_all_invoice_amounts(db)
        anomaly = detect_anomaly(amount, historical)

        # 3. Vendor behavior analysis
        vendor_name = (invoice_data.get("vendor") or {}).get("name", "")
        vendor_history = await get_vendor_invoice_amounts(db, vendor_name)
        vendor_result = analyze_vendor_spend(vendor_name, amount, vendor_history)

        # 4. Duplicate detection
        existing = await get_existing_invoices_for_duplicate_check(db)
        dup_result = check_duplicate(invoice_data, existing)

        # Block save if duplicate found
        if dup_result["is_duplicate"]:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "duplicate_invoice",
                    "message": f"Duplicate invoice detected: {dup_result['reason']}",
                    "matched_invoice_number": dup_result["matched_invoice_number"],
                }
            )

        # 5. Attach analytics metadata before saving
        invoice_data["_analytics"] = {
            "status": validation["status"],
            "issues": validation["issues"],
            "is_anomaly": anomaly["is_anomaly"] or vendor_result["vendor_anomaly"],
            "is_duplicate": dup_result["is_duplicate"],
            "confidence_score": confidence,
        }

        invoice_id = await save_invoice_data(db, invoice_data)

        return {
            "message": "Invoice saved successfully",
            "invoice_header_id": invoice_id,
            "analytics": {
                "validation": validation,
                "confidence_score": confidence,
                "anomaly": anomaly,
                "vendor_analysis": vendor_result,
                "duplicate": dup_result,
            },
        }

    except Exception as e:
        logger.error("Save invoice failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


# ── Analytics endpoint ─────────────────────────────────────────────────────────

@app.get("/analytics")
async def analytics(db: AsyncSession = Depends(get_db)):
    """
    Returns aggregated spend analytics.
    Example response:
    {
        "total_spend": 150000.0,
        "vendor_spend": {"ABC Ltd": 80000.0, "XYZ Corp": 70000.0},
        "monthly_spend": {"2024-01": 50000.0},
        "anomaly_count": 3,
        "faulty_count": 2
    }
    """
    try:
        return await get_analytics_summary(db)
    except Exception as e:
        logger.error("Analytics query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ── Alerts endpoint ────────────────────────────────────────────────────────────

@app.get("/alerts")
async def alerts(db: AsyncSession = Depends(get_db)):
    """
    Returns lists of faulty, anomalous, and duplicate invoices.
    Example response:
    {
        "faulty_invoices": [...],
        "anomalous_invoices": [...],
        "duplicate_invoices": [...]
    }
    """
    try:
        return await get_alerts(db)
    except Exception as e:
        logger.error("Alerts query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
