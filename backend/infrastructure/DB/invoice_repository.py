from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.DB.models import (
    Vendor,
    InvoiceHeader,
    InvoiceItems,
    InvoiceSummary
)
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

def parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()

def safe_decimal(val):
    if val in (None, "", "null"):
        return None
    return Decimal(str(val).replace(",", ""))

def safe_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except:
        return None

def normalize_invoice_data(data: dict) -> dict:
    header = data.get("invoice_header", {})

    header["invoice_date"] = safe_date(header.get("invoice_date"))
    header["due_date"] = safe_date(header.get("due_date"))
    header["invoice_amount"] = safe_decimal(header.get("invoice_amount"))

# 💣 HARD KILL po_references
    raw_po = header.get("po_references")

    if isinstance(raw_po, dict):
        header["po_references"] = raw_po
    else:
        # ANYTHING else (string "null", "", list, int) → None
        header["po_references"] = None

       
    # Items
    for item in data.get("items", []):
        item["rate"] = safe_decimal(item.get("rate"))
        item["billed_qty"] = safe_decimal(item.get("billed_qty"))
        item["taxable_value"] = safe_decimal(item.get("taxable_value"))

    # Summary (guarded)
    summary = data.get("summary")
    if isinstance(summary, dict):
        summary["grand_total"] = safe_decimal(summary.get("grand_total"))

    return data



async def save_invoice_data(db: AsyncSession, invoice_data: dict):
    try:
        # 1️⃣ Vendor
        vendor = Vendor(**invoice_data.get("vendor", {}))
        db.add(vendor)
        await db.flush()

        # 2️⃣ Invoice Header (MANUAL FIELD MAPPING ONLY)
        header    = invoice_data.get("invoice_header", {})
        analytics = invoice_data.get("_analytics", {})

        invoice_header = InvoiceHeader(
            vendor_id=vendor.vendor_id,
            invoice_number=header.get("invoice_number"),
            invoice_date=header.get("invoice_date"),
            due_date=header.get("due_date"),
            invoice_amount=header.get("invoice_amount"),
            ntby_no=header.get("ntby_no"),
            irn=header.get("irn"),
            po_references=None,
            # Analytics columns
            status=analytics.get("status", "valid"),
            issues=analytics.get("issues", []),
            is_anomaly=analytics.get("is_anomaly", False),
            is_duplicate=analytics.get("is_duplicate", False),
            confidence_score=analytics.get("confidence_score"),
        )

        db.add(invoice_header)
        await db.flush()

        # 3️⃣ Items
        for item in invoice_data.get("items", []):
             invoice_item = InvoiceItems(
        invoice_header_id=invoice_header.invoice_header_id,
        code=item.get("code"),
        description=item.get("description"),
        uom=item.get("uom"),
        billed_qty=item.get("billed_qty"),
        rate=item.get("rate"),
        discount_percent=item.get("discount_percent"),
        discount_amount=item.get("discount_amount"),
        taxable_value=item.get("taxable_value"),
        hsn_code=item.get("hsn_code"),
        cgst_percent=item.get("cgst_percent"),
        cgst_amount=item.get("cgst_amount"),
        sgst_percent=item.get("sgst_percent"),
        sgst_amount=item.get("sgst_amount"),
        igst_percent=item.get("igst_percent"),
        igst_amount=item.get("igst_amount"),
        roundoff=item.get("roundoff"),
        total_value=item.get("total_value"),)
             db.add(invoice_item)


        # 4️⃣ Summary
        summary = invoice_data.get("summary", {})
        invoice_summary = InvoiceSummary(
               invoice_header_id=invoice_header.invoice_header_id,
               product_total=summary.get("product_total"),
               taxable_value_total=summary.get("taxable_value_total"),
               freight_charges=summary.get("freight_charges"),
               cgst_total=summary.get("cgst_total"),
               sgst_total=summary.get("sgst_total"),
               igst_total=summary.get("igst_total"),
               tcs_percent=summary.get("tcs_percent"),
               tcs_amount=summary.get("tcs_amount"),
               roundoff_amount=summary.get("roundoff_amount"),
               grand_total=summary.get("grand_total"),
               buyer_name=summary.get("buyer_name"),
)
        db.add(invoice_summary)


        await db.commit()
        return invoice_header.invoice_header_id

    except Exception as e:
        await db.rollback()
        raise e


# ── Analytics queries ──────────────────────────────────────────────────────────

async def get_all_invoice_amounts(db: AsyncSession) -> list[float]:
    """Returns all invoice amounts for global anomaly detection."""
    result = await db.execute(
        select(InvoiceHeader.invoice_amount).where(InvoiceHeader.invoice_amount.isnot(None))
    )
    return [float(row[0]) for row in result.fetchall()]


async def get_vendor_invoice_amounts(db: AsyncSession, vendor_name: str) -> list[float]:
    """Returns historical invoice amounts for a specific vendor."""
    result = await db.execute(
        select(InvoiceHeader.invoice_amount)
        .join(Vendor, Vendor.vendor_id == InvoiceHeader.vendor_id)
        .where(Vendor.name == vendor_name, InvoiceHeader.invoice_amount.isnot(None))
    )
    return [float(row[0]) for row in result.fetchall()]


async def get_existing_invoices_for_duplicate_check(db: AsyncSession) -> list[dict]:
    """Returns minimal invoice data needed for duplicate detection."""
    result = await db.execute(
        select(
            Vendor.name.label("vendor_name"),
            InvoiceHeader.invoice_amount,
            InvoiceHeader.invoice_date,
            InvoiceHeader.invoice_number,
        ).join(Vendor, Vendor.vendor_id == InvoiceHeader.vendor_id)
    )
    return [
        {
            "vendor_name": row.vendor_name,
            "invoice_amount": float(row.invoice_amount) if row.invoice_amount else None,
            "invoice_date": str(row.invoice_date) if row.invoice_date else None,
            "invoice_number": row.invoice_number,
        }
        for row in result.fetchall()
    ]


async def get_analytics_summary(db: AsyncSession) -> dict:
    """Aggregated data for the /analytics endpoint."""
    from sqlalchemy import func

    # Total spend
    total = await db.execute(select(func.sum(InvoiceHeader.invoice_amount)))
    total_spend = float(total.scalar() or 0)

    # Vendor-wise spend
    vendor_spend_rows = await db.execute(
        select(Vendor.name, func.sum(InvoiceHeader.invoice_amount).label("total"))
        .join(Vendor, Vendor.vendor_id == InvoiceHeader.vendor_id)
        .group_by(Vendor.name)
    )
    vendor_spend = {row.name: float(row.total or 0) for row in vendor_spend_rows.fetchall()}

    # Monthly spend
    monthly_rows = await db.execute(
        select(
            func.to_char(InvoiceHeader.invoice_date, "YYYY-MM").label("month"),
            func.sum(InvoiceHeader.invoice_amount).label("total"),
        )
        .where(InvoiceHeader.invoice_date.isnot(None))
        .group_by("month")
        .order_by("month")
    )
    monthly_spend = {row.month: float(row.total or 0) for row in monthly_rows.fetchall()}

    # Counts
    anomaly_count = await db.execute(
        select(func.count()).where(InvoiceHeader.is_anomaly == True)
    )
    faulty_count = await db.execute(
        select(func.count()).where(InvoiceHeader.status == "faulty")
    )

    return {
        "total_spend": total_spend,
        "vendor_spend": vendor_spend,
        "monthly_spend": monthly_spend,
        "anomaly_count": int(anomaly_count.scalar() or 0),
        "faulty_count": int(faulty_count.scalar() or 0),
    }


async def get_alerts(db: AsyncSession) -> dict:
    """Returns lists of faulty, anomalous, and duplicate invoices."""
    def _row_to_dict(row):
        return {
            "invoice_header_id": row.invoice_header_id,
            "invoice_number": row.invoice_number,
            "invoice_amount": float(row.invoice_amount) if row.invoice_amount else None,
            "status": row.status,
            "issues": row.issues,
            "is_anomaly": row.is_anomaly,
            "is_duplicate": row.is_duplicate,
            "confidence_score": row.confidence_score,
        }

    faulty = await db.execute(
        select(InvoiceHeader).where(InvoiceHeader.status == "faulty")
    )
    anomalous = await db.execute(
        select(InvoiceHeader).where(InvoiceHeader.is_anomaly == True)
    )
    duplicates = await db.execute(
        select(InvoiceHeader).where(InvoiceHeader.is_duplicate == True)
    )

    return {
        "faulty_invoices": [_row_to_dict(r) for r in faulty.scalars().all()],
        "anomalous_invoices": [_row_to_dict(r) for r in anomalous.scalars().all()],
        "duplicate_invoices": [_row_to_dict(r) for r in duplicates.scalars().all()],
    }
