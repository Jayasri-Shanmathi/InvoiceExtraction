from sqlalchemy import Column,Integer,String,Text,Date,ForeignKey,Numeric,JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Vendor(Base):
    __tablename__="vendor"
    __table_args__={"schema":"public"}
    vendor_id=Column(Integer,primary_key=True,index=True)
    name=Column(String(255))
    address=Column(Text)
    email=Column(String(255))
    gst_no=Column(String(100))
    contact=Column(String(100))

    invoices = relationship("InvoiceHeader", back_populates="vendor")

class InvoiceHeader(Base):
        __tablename__="invoice_headers"
        __table_args__={"schema":"public"}

        invoice_header_id=Column(Integer,primary_key=True,index=True)
        vendor_id=Column(Integer,ForeignKey("public.vendor.vendor_id"))
        invoice_number=Column(String(100))
        invoice_date=Column(Date)
        due_date=Column(Date)
        invoice_amount=Column(Numeric(12,2))
        ntby_no=Column(String(100))
        po_references=Column(JSON,nullable=True)
        irn=Column(String(255))

        vendor=relationship("Vendor",back_populates="invoices")
        invoice_items = relationship("InvoiceItems", back_populates="invoice")
        invoice_summary = relationship("InvoiceSummary", back_populates="invoice", uselist=False)


class InvoiceItems(Base):
      __tablename__="invoice_items"
      __table_args__={"schema":"public"}

      item_id=Column(Integer,primary_key=True)
      invoice_header_id=Column(Integer,ForeignKey("public.invoice_headers.invoice_header_id"))
      code=Column(String(100))
      description=Column(Text)
      uom=Column(String(50))
      billed_qty=Column(Numeric(12,2))
      rate=Column(Numeric(12,2))
      discount_percent=Column(Numeric(12,2))
      discount_amount=Column(Numeric(12,2))
      taxable_value=Column(Numeric(12,2))
      hsn_code=Column(String(50))
      cgst_percent=Column(Numeric(12,2))
      cgst_amount=Column(Numeric(12,2))
      sgst_percent=Column(Numeric(12,2))
      sgst_amount=Column(Numeric(12,2))
      igst_percent=Column(Numeric(12,2))
      igst_amount=Column(Numeric(12,2))
      roundoff=Column(Numeric(12,2))
      total_value=Column(Numeric(12,2))

      invoice=relationship("InvoiceHeader",back_populates="invoice_items")

class InvoiceSummary(Base):
      __tablename__="invoice_summary"
      __table_args__={"schema":"public"}
      invoice_summary_id=Column(Integer,primary_key=True)
      invoice_header_id=Column(Integer,ForeignKey("public.invoice_headers.invoice_header_id"))
      product_total=Column(Numeric(12,2))
      taxable_value_total=Column(Numeric(12,2))
      freight_charges=Column(Numeric(12,2))
      cgst_total=Column(Numeric(12,2))
      sgst_total=Column(Numeric(12,2))
      igst_total=Column(Numeric(12,2))
      tcs_percent=Column(Numeric(12,2))
      tcs_amount=Column(Numeric(12,2))
      roundoff_amount=Column(Numeric(12,2))
      grand_total=Column(Numeric(12,2))
      buyer_name=Column(String(255))

      invoice=relationship("InvoiceHeader",back_populates="invoice_summary")
      