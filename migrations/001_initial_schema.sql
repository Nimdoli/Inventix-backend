-- Run this in Supabase's SQL Editor (or via Alembic once configured) to create
-- all tables. Matches app/models/models.py exactly.

create table if not exists profiles (
  id uuid references auth.users primary key,
  full_name text,
  role text check (role in ('customer', 'supplier')),
  store_name text,
  contact_number text
);

create table if not exists products (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references profiles(id),
  name text not null,
  category text not null,
  price numeric not null,
  stock int not null,
  status text check (status in ('in_stock', 'low_stock', 'out_of_stock')),
  created_at timestamptz default now()
);

create table if not exists orders (
  id text primary key,
  customer_id uuid references profiles(id),
  store text not null,
  amount numeric not null,
  location text,
  item_count int,
  status text check (status in ('pending', 'delivered')),
  order_date date not null default current_date
);

create table if not exists deliveries (
  id text primary key,
  order_id text references orders(id),
  company text not null,
  shipped_date date,
  eta_date date,
  status text check (status in ('pending', 'in_transit', 'delivered'))
);

create table if not exists suppliers (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  address text,
  phone text,
  email text,
  is_active boolean default true
);

create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  category text check (category in ('sales', 'inventory')),
  file_name text not null,
  file_url text,
  generated_at timestamptz default now()
);

create table if not exists purchase_orders (
  id uuid primary key default gen_random_uuid(),
  product_id uuid references products(id),
  supplier_id uuid references suppliers(id),
  status text default 'draft' check (status in ('draft', 'sent', 'approved')),
  quantity int,
  created_at timestamptz default now()
);

-- Auto-create a profile row whenever someone registers via Supabase Auth.
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, full_name, role)
  values (new.id, new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'role');
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
