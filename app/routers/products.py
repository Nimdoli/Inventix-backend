import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut

router = APIRouter(prefix="/product", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    category: Optional[str] = None,  # "in stock" | "low stock"
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    query = db.query(Product)
    if category == "in stock":
        query = query.filter(Product.status == "in_stock")
    elif category == "low stock":
        query = query.filter(Product.status == "low_stock")
    return query.all()


@router.get("/search", response_model=list[ProductOut])
def search_products(
    category: Optional[str] = None,  # "groceries" | "dairy" etc.
    query: Optional[str] = None,     # free-text name search
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    q = db.query(Product)
    if category:
        q = q.filter(Product.category.ilike(category))
    if query:
        q = q.filter(Product.name.ilike(f"%{query}%"))
    return q.all()


@router.post("", response_model=ProductOut, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    product = Product(**payload.model_dump(), owner_id=user["sub"])
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
