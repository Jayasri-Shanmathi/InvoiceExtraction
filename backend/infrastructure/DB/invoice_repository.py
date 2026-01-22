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
        header = invoice_data.get("invoice_header", {})

        invoice_header = InvoiceHeader(
            vendor_id=vendor.vendor_id,
            invoice_number=header.get("invoice_number"),
            invoice_date=header.get("invoice_date"),
            due_date=header.get("due_date"),
            invoice_amount=header.get("invoice_amount"),
            ntby_no=header.get("ntby_no"),
            irn=header.get("irn"),

            # 🚨 FORCE JSON NULL
            po_references=None
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
