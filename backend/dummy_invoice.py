DUMMY_INVOICE_DATA = {
    "vendor": {
        "name": "ABC Technologies Pvt Ltd",
        "address": "No 45, Anna Nagar, Chennai, Tamil Nadu - 600040",
        "email": "billing@abctech.com",
        "gst_no": "33ABCDE1234F1Z5",
        "contact": "+91 9876543210"
    },
    "invoice_header": {
        "invoice_number": "INV-102454",
        "invoice_date": "2023-08-24",
        "due_date": "2023-09-24",
        "invoice_amount": 68239.00,
        "ntby_no": None,
        "po_references": {"po_number": "PO-88991"},
        "irn": None
    },
    "items": [
        {
            "code": "PRD001",
            "description": "Laptop – Dell Inspiron 15",
            "uom": "Nos",
            "billed_qty": 2,
            "rate": 30000,
            "discount_percent": 5,
            "discount_amount": 3000,
            "taxable_value": 57000,
            "hsn_code": "84713010",
            "cgst_percent": 9,
            "cgst_amount": 5130,
            "sgst_percent": 9,
            "sgst_amount": 5130,
            "igst_percent": None,
            "igst_amount": None,
            "roundoff": 0,
            "total_value": 67260
        }
    ],
    "summary": {
        "product_total": 60000,
        "taxable_value_total": 57000,
        "freight_charges": 0,
        "cgst_total": 5130,
        "sgst_total": 5130,
        "igst_total": 0,
        "tcs_percent": None,
        "tcs_amount": None,
        "roundoff_amount": -21,
        "grand_total": 68239,
        "buyer_name": "XYZ Solutions Pvt Ltd"
    }
}
