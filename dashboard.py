import streamlit as st
import pandas as pd
import csv
import os
import datetime
st.set_option("client.showErrorDetails", True)


INVENTORY_FILE = "inventory.csv"
SALES_FILE = "sales.csv"

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        return []
    with open(INVENTORY_FILE, mode='r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_inventory(data):
    with open(INVENTORY_FILE, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["item", "company", "model", "stock", "price", "reorder_level"])
        writer.writeheader()
        writer.writerows(data)

def record_sale_to_file(item, company, model, qty_sold, price):
    total = qty_sold * price
    sale_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = os.path.isfile(SALES_FILE)
    with open(SALES_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["item", "company", "model", "quantity", "price", "total", "sale_time"])
        writer.writerow([item, company, model, qty_sold, price, total, sale_time])

# Load and prepare data
df = pd.DataFrame(load_inventory())
if not df.empty:
    for col in ["stock", "price", "reorder_level"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
# --- Check for low-stock alerts ---
low_stock_df = df[df["stock"] < df["reorder_level"]]

if not low_stock_df.empty:
    st.warning("⚠️ The following items are below their reorder level:")
    st.dataframe(low_stock_df[["item", "company", "model", "stock", "reorder_level"]])


st.title("🛒 Stationery Inventory Management")

# --- Display Inventory ---
st.subheader("📦 Current Inventory")
st.dataframe(df)

# --- Add New Item ---
st.subheader("➕ Add New Item")
with st.form("add_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        item = st.text_input("Item")
    with col2:
        company = st.text_input("Company")
    with col3:
        model = st.text_input("Model")

    col4, col5, col6 = st.columns(3)
    with col4:
        stock = st.number_input("Stock", min_value=0, step=1)
    with col5:
        price = st.number_input("Price", min_value=0.0, step=0.1)
    with col6:
        reorder_level = st.number_input("Reorder Level", min_value=0, step=1)

    add_submit = st.form_submit_button("Add Item")

    if add_submit and item and company:
        inventory = load_inventory()
        inventory.append({
            "item": item,
            "company": company,
            "model": model,
            "stock": stock,
            "price": price,
            "reorder_level": reorder_level
        })
        save_inventory(inventory)
        st.success(f"Item '{item}' added successfully!")
        st.experimental_rerun()

# --- Record Sale ---
st.subheader("🧾 Record Sale")

if not df.empty:
    sale_item = st.selectbox("Item", df["item"].unique(), key="sale_item")
    filtered_companies = df[df["item"] == sale_item]["company"].unique()
    sale_company = st.selectbox("Company", filtered_companies, key="sale_company")
    filtered_models = df[(df["item"] == sale_item) & (df["company"] == sale_company)]["model"].unique()
    sale_model = st.selectbox("Model", filtered_models, key="sale_model")

    qty_sold = st.number_input("Quantity Sold", min_value=1, step=1)

    if st.button("Record Sale"):
        inventory = load_inventory()
        for row in inventory:
            if (row['item'] == sale_item and row['company'] == sale_company and row['model'] == sale_model):
                row['stock'] = str(max(0, int(row['stock']) - int(qty_sold)))
                price = float(row['price'])
                record_sale_to_file(sale_item, sale_company, sale_model, qty_sold, price)
                break
        save_inventory(inventory)
        st.success(f"Recorded sale of {qty_sold} {sale_item}(s)")
        st.experimental_rerun()

# --- Update Price ---
st.subheader("💰 Update Item Price")

if not df.empty:
    price_item = st.selectbox("Item", df["item"].unique(), key="p_item")
    filtered_companies = df[df["item"] == price_item]["company"].unique()
    price_company = st.selectbox("Company", filtered_companies, key="p_company")
    filtered_models = df[(df["item"] == price_item) & (df["company"] == price_company)]["model"].unique()
    price_model = st.selectbox("Model", filtered_models, key="p_model")

    new_price = st.number_input("New Price", min_value=0.0, step=0.1)

    if st.button("Update Price"):
        inventory = load_inventory()
        found = False
        for row in inventory:
            if (row['item'] == price_item and row['company'] == price_company and row['model'] == price_model):
                row['price'] = str(new_price)
                found = True
                break
        if found:
            save_inventory(inventory)
            st.success(f"Updated price for {price_item} to ₹{new_price:.2f}")
            st.experimental_rerun()
        else:
            st.error("Item not found.")

# --- Delete Item ---
st.subheader("🗑️ Delete Item")

if not df.empty:
    del_item = st.selectbox("Item", df["item"].unique(), key="d_item")
    filtered_companies = df[df["item"] == del_item]["company"].unique()
    del_company = st.selectbox("Company", filtered_companies, key="d_company")
    filtered_models = df[(df["item"] == del_item) & (df["company"] == del_company)]["model"].unique()
    del_model = st.selectbox("Model", filtered_models, key="d_model")

    if st.button("Delete Item"):
        inventory = load_inventory()
        inventory = [row for row in inventory if not (
            row['item'] == del_item and row['company'] == del_company and row['model'] == del_model)]
        save_inventory(inventory)
        st.success(f"Deleted {del_item} from inventory.")
        st.experimental_rerun()

# --- Show Today's Sales ---
st.subheader("📅 Today's Sales")
if os.path.exists(SALES_FILE) and os.path.getsize(SALES_FILE) > 0:
    try:
        sales_df = pd.read_csv(SALES_FILE)
        sales_df['sale_time'] = pd.to_datetime(sales_df['sale_time'])
        today = pd.to_datetime(datetime.datetime.now().date())
        todays_sales = sales_df[sales_df['sale_time'].dt.date == today.date()]

        if not todays_sales.empty:
            st.dataframe(todays_sales)
            total_today = todays_sales["total"].sum()
            st.success(f"Total Sales Today: ₹{total_today}")
        else:
            st.info("No sales recorded today.")
    except Exception as e:
        st.error(f"Error loading sales file: {e}")
else:
    st.info("No sales have been recorded yet.")
