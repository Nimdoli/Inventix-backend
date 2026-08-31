from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import products, orders, delivery, suppliers, reports, purchase_orders, analytics, users

app = FastAPI(title="InventiX API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual client origins before production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(analytics.router)
app.include_router(orders.router)
app.include_router(delivery.router)
app.include_router(suppliers.router)
app.include_router(reports.router)
app.include_router(purchase_orders.router)


@app.get("/")
def root():
    return {"status": "InventiX API is running"}
