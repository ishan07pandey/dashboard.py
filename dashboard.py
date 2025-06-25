import streamlit as st
import pandas as pd
import csv
import os

INVENTORY_FILE = "inventory.csv"

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

# Load and prepare data
df = pd.DataFrame(load_inventory())
if not df.empty:
    for col in ["stock", "price", "reorder_level"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

st.title("🛒 Stationery Inventory Management")

# Display inventory
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
        stock = st.number_input("stock", min_value=0, step=1)
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
with st.form("sale_form"):
    if not df.empty:
        sale_item = st.selectbox("Item", df["item"].unique())
        sale_company_df = df[df["item"] == sale_item]
        sale_company = st.selectbox("Company", df["company"].unique())
        sale_model_df = sale_company_df[df["company"] == sale_company]
        sale_model = st.selectbox("Model", df["model"].unique())

        qty_sold = st.number_input("stock Sold", min_value=1, step=1)
        sale_submit = st.form_submit_button("Record Sale")

        if sale_submit:
            inventory = load_inventory()
            for row in inventory:
                if (row['item'] == sale_item and row['company'] == sale_company and row['model'] == sale_model):
                    row['stock'] = str(max(0, int(row['quantity']) - int(qty_sold)))
                    break
            save_inventory(inventory)
            st.success(f"Recorded sale of {qty_sold} {sale_item}(s)")
            st.experimental_rerun()

# --- Update Price ---
st.subheader("💰 Update Item Price")
with st.form("update_price_form"):
    if not df.empty:
        price_item = st.selectbox("Item", df["item"].unique(), key="p_item")
        price_company_df = df[df["item"] == price_item]
        price_company = st.selectbox("Company",df["company"].unique(), key="p_company")
        price_model_df = price_company_df[df["company"] == price_company]
        price_model = st.selectbox("Model",df["model"].unique(), key="p_model")

        new_price = st.number_input("New Price", min_value=0.0, step=0.1)
        price_submit = st.form_submit_button("Update Price")

        if price_submit:
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
with st.form("delete_form"):
    if not df.empty:
        del_item = st.selectbox("Item", df["item"].unique(), key="d_item")
        del_company_df = df[df["item"] == del_item]
        del_company = st.selectbox("Company",df["company"].unique(), key="d_company")
        del_model_df = del_company_df[df["company"] == del_company]
        del_model = st.selectbox("Model",df["model"].unique(), key="d_model")

        del_submit = st.form_submit_button("Delete Item")
        if del_submit:
            inventory = load_inventory()
            inventory = [row for row in inventory if not (
                row['item'] == del_item and row['company'] == del_company and row['model'] == del_model)]
            save_inventory(inventory)
            st.success(f"Deleted {del_item} from inventory.")
            st.experimental_rerun()
