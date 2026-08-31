from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import Delivery

router = APIRouter(prefix="/delivery", tags=["delivery"])

STATUS_MAP = {
    "pending": "pending",
    "in transit": "in_transit",
    "delivered": "delivered",
}


class DeliveryBase(BaseModel):
    company: str
    shipped_date: Optional[date] = None
    eta_date: Optional[date] = None
    status: str  # "pending" | "in_transit" | "delivered"


class DeliveryCreate(DeliveryBase):
    id: str  # "#DEL-0002"
    order_id: Optional[str] = None


class DeliveryUpdate(BaseModel):
    status: Optional[str] = None
    eta_date: Optional[date] = None


class DeliveryOut(DeliveryBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    order_id: Optional[str] = None


@router.get("", response_model=list[DeliveryOut])
def list_deliveries(
    category: Optional[str] = None,  # "pending" | "in transit" | "delivered"
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Delivery)
    if category in STATUS_MAP:
        query = query.filter(Delivery.status == STATUS_MAP[category])
    return query.all()


@router.get("/search", response_model=list[DeliveryOut])
def search_deliveries(
    query: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return db.query(Delivery).filter(Delivery.company.ilike(f"%{query}%")).all()


@router.post("", response_model=DeliveryOut, status_code=201)
def create_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    delivery = Delivery(**payload.model_dump())
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery


@router.put("/{delivery_id}", response_model=DeliveryOut)
def update_delivery(
    delivery_id: str,
    payload: DeliveryUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(delivery, field, value)
    db.commit()
    db.refresh(delivery)
    return delivery
