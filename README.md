# InventiX Backend

FastAPI backend for the InventiX Android app. Auth (login/register/password reset) is
handled directly by Supabase Auth from the Android app via the Supabase client SDK —
this API only owns the business data (products, orders, delivery, suppliers, reports,
purchase orders) and verifies the Supabase-issued JWT on every request.

## Setup

1. **Create a Supabase project** at supabase.com if you haven't already.
2. **Run the schema**: open the SQL Editor in your Supabase project and run
   `migrations/001_initial_schema.sql`.
3. **Copy `.env.example` to `.env`** and fill in your real values from:
   - Settings → Database → Connection string (`DATABASE_URL`)
   - Settings → API → Project URL (`SUPABASE_URL`) and JWT Secret (`SUPABASE_JWT_SECRET`)
4. **Install dependencies** (Python 3.11+ recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   pip install -r requirements.txt
   ```
5. **Run it**:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Open `http://localhost:8000/docs` — FastAPI's auto-generated Swagger UI. Every
   endpoint below is listed there and can be tested directly (you'll need a valid
   Supabase JWT — get one by logging in via the Supabase client SDK, or via
   Supabase's REST auth endpoint directly for testing).

## Endpoints implemented

- `GET/PUT /user/profile`
- `GET/POST/PUT/DELETE /product`, `GET /product/search`
- `GET /analytics/stock-overview`
- `GET/POST/PUT /orders`, `GET /orders/search`
- `GET/POST/PUT /delivery`, `GET /delivery/search`
- `GET/POST/PUT/DELETE /suppliers`, `GET /suppliers/search`
- `GET/POST /reports`, `GET /reports/{id}/download`, `POST /reports/schedule`
- `POST /purchase-orders/generate`, `PUT /purchase-orders/{id}`,
  `POST /purchase-orders/{id}/send`, `GET /purchase-orders/suggest-supplier/{productId}`

Not implemented here (handled by Supabase Auth directly, or still placeholders):
- `login` / `register` / `forgot-password` / `reset-password` — call Supabase Auth
  directly from the Android app instead.
- `change-password` — also a direct Supabase Auth SDK call
  (`supabase.auth.updateUser`).
- `notifications` — no notifications table/feature exists yet.
- `suggest-supplier` currently returns the first active supplier as a placeholder —
  replace with real ranking logic once you have delivery-performance/price data to
  rank suppliers by.

## Next steps

- Wire the Android app's Retrofit client to this base URL (`http://10.0.2.2:8000` from
  an emulator, since `localhost` on the emulator refers to the emulator itself, not
  your host machine).
- Add the Supabase client SDK to the Android app for Auth (login/register/password
  reset) — this backend never sees passwords, it only verifies the JWT Supabase
  already issued.
- Replace `MockData.kt`'s static lists with real API calls, screen by screen, starting
  with Products.
