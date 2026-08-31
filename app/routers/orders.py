from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import Order

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderBase(BaseModel):
    store: str
    amount: float
    location: Optional[str] = None
    item_count: Optional[int] = None
    status: str  # "pending" | "delivered"


class OrderCreate(OrderBase):
    id: str  # "#ORD-0001" — client-generated to match the display format


class OrderUpdate(BaseModel):
    status: Optional[str] = None


class OrderOut(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


@router.get("", response_model=list[OrderOut])
def list_orders(
    category: Optional[str] = None,  # "pending" | "delivered"
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Order)
    if category in ("pending", "delivered"):
        query = query.filter(Order.status == category)
    return query.all()


@router.get("/search", response_model=list[OrderOut])
def search_orders(
    query: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return db.query(Order).filter(Order.store.ilike(f"%{query}%")).all()


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    order = Order(**payload.model_dump(), customer_id=user["sub"])
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}", response_model=OrderOut)
def update_order(
    order_id: str,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order
