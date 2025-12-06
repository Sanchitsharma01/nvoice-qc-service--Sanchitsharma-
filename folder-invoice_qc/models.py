from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class LineItem(BaseModel):
    description: str = Field(..., description="Item name or description")
    quantity: float = Field(..., ge=0)
    unit_price: float = Field(..., ge=0)
    line_total: float = Field(..., ge=0)

class InvoiceTotals(BaseModel):
    net_amount: float = Field(..., ge=0, description="Gesamtwert excluding tax")
    tax_amount: float = Field(..., ge=0, description="MwSt amount")
    gross_amount: float = Field(..., ge=0, description="Gesamtwert including tax")

class Invoice(BaseModel):
    invoice_number: str = Field(..., description="The AUFNR number")
    invoice_date: date
    due_date: Optional[date] = None
    
    seller_name: Optional[str] = Field(None, description="Name of the vendor")
    seller_address: Optional[str] = None
    
    buyer_name: Optional[str] = Field(None, description="Name of the customer")
    buyer_address: Optional[str] = None
    
    currency: str = Field("EUR", pattern="^[A-Z]{3}$")
    
    totals: InvoiceTotals
    line_items: List[LineItem] = []
