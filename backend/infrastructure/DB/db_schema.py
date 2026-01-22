from pydantic import BaseModel,EmailStr
from typing import Optional
from decimal import Decimal
from datetime import date
class VendorBase(BaseModel):
    name:Optional[str]
    address:Optional[str]
    email:Optional[str]
    gst_no:Optional[str]
    contact:Optional[str]

class InvoiceItemBase(BaseModel):
    code:Optional[str]
    description:Optional[str]
    uom:Optional[str]         
    billed_qty:Optional[Decimal]
    rate:Optional[Decimal]   
    discount_percent:Optional[Decimal]
    discount_amount:Optional[Decimal]
    taxable_value:Optional[Decimal]
    hsn_code:Optional[str]
    cgst_percent:Optional[Decimal]
    cgst_amount:Optional[Decimal]
    sgst_percent:Optional[Decimal]
    sgst_amount:Optional[Decimal]
    igst_percent:Optional[Decimal]
    igst_amount:Optional[Decimal]
    roundoff:Optional[Decimal]
    total_value:Optional[Decimal]

class InvoiceSummaryBase(BaseModel):
        product_total:Optional[Decimal]
        taxable_value_total:Optional[Decimal]
        freight_charges:Optional[Decimal]
        tax_percentage:Optional[Decimal]
        cgst_total:Optional[Decimal]
        sgst_total:Optional[Decimal]
        igst_total:Optional[Decimal]
        tcs_percent:Optional[Decimal]
        tcs_amount:Optional[Decimal]
        roundoff_amount:Optional[Decimal]
        grand_total:Optional[Decimal]
        buyer_name:Optional[str]

class InvoiceHeaderBase(BaseModel):
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    due_date: Optional[date]
    invoice_amount: Optional[Decimal]
    ntby_no: Optional[str]
    po_references: Optional[dict]
    irn: Optional[str]


#class VendorCreate(VendorBase):
#    pass
# class VendorResponse(VendorBase):
#    vendor_id:int
#     class Config:
#         from_attributes=True
