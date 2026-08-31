import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import PurchaseOrder, Product, Supplier

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


class GenerateRequest(BaseModel):
    product_id: uuid.UUID
    supplier_id: Optional[uuid.UUID] = None  # omit to auto-pick via suggest-supplier first
    quantity: int


class PurchaseOrderUpdate(BaseModel):
    quantity: Optional[int] = None
    status: Optional[str] = None


class PurchaseOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    supplier_id: Optional[uuid.UUID] = None
    status: str
    quantity: Optional[int] = None


@router.post("/generate", response_model=PurchaseOrderOut, status_code=201)
def generate_purchase_order(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    po = PurchaseOrder(
        product_id=payload.product_id,
        supplier_id=payload.supplier_id,
        quantity=payload.quantity,
        status="draft",
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po


@router.put("/{po_id}", response_model=PurchaseOrderOut)
def update_purchase_order(
    po_id: uuid.UUID,
    payload: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(po, field, value)
    db.commit()
    db.refresh(po)
    return po


@router.post("/{po_id}/send", response_model=PurchaseOrderOut)
def send_purchase_order(
    po_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    po.status = "sent"
    db.commit()
    db.refresh(po)
    return po
    # TODO: actually notify the supplier (email via Supabase, or a notifications table)


@router.get("/suggest-supplier/{product_id}")
def suggest_supplier(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    # Placeholder ranking: first active supplier. Replace with real ranking logic
    # (price history, delivery reliability, etc.) once that data exists.
    supplier = db.query(Supplier).filter(Supplier.is_active.is_(True)).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="No active suppliers available")
    return {
        "supplier_id": supplier.id,
        "name": supplier.name,
        "reason": "Active supplier with fastest historical delivery (placeholder logic)",
    }
