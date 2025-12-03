from pydantic import BaseModel
from typing import Optional


class ReceiptData(BaseModel):
    date: Optional[str] = None
    amount: float = 0.0
    category: str = "Other"


class ReceiptResponse(BaseModel):
    status: str
    data: ReceiptData
    error: Optional[str] = None
