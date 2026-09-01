import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    # No status field — it's computed automatically from stock, not client-supplied.


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    # status intentionally omitted — always derived from stock, never set directly.


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    category: str
    price: float
    stock: int
    status: str  # "in_stock" | "low_stock" | "out_of_stock" — computed, read-only
    owner_id: Optional[uuid.UUID] = None
