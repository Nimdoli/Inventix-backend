import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import Supplier

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


class SupplierBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierOut(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


@router.get("", response_model=list[SupplierOut])
def list_suppliers(
    category: Optional[str] = None,  # "company" | "products" — sort/grouping hint
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Supplier)
    if category == "company":
        query = query.order_by(Supplier.name)
    return query.all()


@router.get("/search", response_model=list[SupplierOut])
def search_suppliers(
    query: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return db.query(Supplier).filter(Supplier.name.ilike(f"%{query}%")).all()


@router.post("", response_model=SupplierOut, status_code=201)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(
    supplier_id: uuid.UUID,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(
    supplier_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
