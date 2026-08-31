from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.models import Product

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/stock-overview")
def stock_overview(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """Powers the Products screen's donut chart. Computed live from the products
    table rather than stored, so it's always accurate."""
    rows = (
        db.query(Product.status, func.count(Product.id))
        .group_by(Product.status)
        .all()
    )
    counts = {status: count for status, count in rows}
    total = sum(counts.values())

    def segment(label: str, key: str):
        value = counts.get(key, 0)
        percent = round((value / total) * 100, 1) if total else 0.0
        return {"label": label, "value": value, "percent": percent}

    return {
        "total": total,
        "segments": [
            segment("In stock", "in_stock"),
            segment("Low stock", "low_stock"),
            segment("Out of stock", "out_of_stock"),
        ],
    }
