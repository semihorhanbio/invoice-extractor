from pydantic import BaseModel, Field
from typing import List, Optional


class InvoiceLine(BaseModel):
    goods_and_services_name: Optional[str] = Field(
        "no value", description="Name of the goods or services."
    )
    goods_and_services_quantity: Optional[int] = Field(
        "no value", description="Quantity of the goods or services."
    )
    goods_and_services_unit_price: Optional[float] = Field(
        "no value", description="Unit price of the goods or services."
    )
    goods_and_services_vat_rate: Optional[float] = Field(
        "no value", description="VAT rate for the goods or services."
    )
    goods_and_services_total: Optional[float] = Field(
        "no value", description="Total price for the goods or services."
    )


class Invoice(BaseModel):
    customer_name: Optional[str] = Field(
        "no value", description="Name of the customer."
    )
    customer_vkn: Optional[int] = Field(
        "no value", description="Tax ID (VKN) of the customer."
    )
    customer_tckn: Optional[int] = Field(
        "no value", description="National ID (TCKN) of the customer."
    )
    vendor_name: Optional[str] = Field("no value", description="Name of the vendor.")
    vendor_vkn: Optional[int] = Field(
        "no value", description="Tax ID (VKN) of the vendor."
    )
    vendor_tckn: Optional[int] = Field(
        "no value", description="National ID (TCKN) of the vendor."
    )
    invoice_senario: Optional[str] = Field(
        "no value", description="Scenario for the invoice."
    )
    invoice_type: Optional[str] = Field("no value", description="Type of the invoice.")
    invoice_no: Optional[str] = Field("no value", description="Invoice number.")
    invoice_date: Optional[str] = Field("no value", description="Date of the invoice.")
    total_of_goods_and_services: Optional[float] = Field(
        "no value", description="Total value of goods and services."
    )
    calculated_vat: Optional[float] = Field(
        "no value", description="Calculated VAT amount."
    )
    invoice_total: Optional[float] = Field(
        "no value", description="Total invoice amount."
    )
    invoice_lines: List[InvoiceLine] = Field(
        default_factory=list, description="List of invoice lines."
    )
