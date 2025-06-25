import csv
import os
from datetime import datetime

INVENTORY_FILE = "inventory.csv"
SALES_FILE = "sales.csv"

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["item", "company", "model", "stock", "price", "reorder_level"])
        return []
    with open(INVENTORY_FILE, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_inventory(data):
    with open(INVENTORY_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "company", "model", "stock", "price", "reorder_level"])
        writer.writeheader()
        writer.writerows(data)

def add_or_update_item(item, company, model, stock, price, reorder_level):
    data = load_inventory()
    stock = int(stock)
    price = float(price)
    reorder_level = int(reorder_level)
    found = False
    for row in data:
        if (row['item'].lower() == item.lower() and
            row['company'].lower() == company.lower() and
            row['model'].lower() == model.lower()):
            # Update existing
            row['stock'] = str(stock)
            row['price'] = str(price)
            row['reorder_level'] = str(reorder_level)
            found = True
            break
    if not found:
        data.append({
            "item": item,
            "company": company,
            "model": model,
            "stock": str(stock),
            "price": str(price),
            "reorder_level": str(reorder_level)
        })
    save_inventory(data)

def update_stock(item, company, model, qty, action):
    # action: "add" or "subtract"
    data = load_inventory()
    qty = int(qty)
    for row in data:
        if (row['item'].lower() == item.lower() and
            row['company'].lower() == company.lower() and
            row['model'].lower() == model.lower()):
            current_stock = int(row['stock'])
            if action == "add":
                current_stock += qty
            elif action == "subtract":
                current_stock = max(current_stock - qty, 0)
            row['stock'] = str(current_stock)
            break
    save_inventory(data)

def delete_item(item, company, model):
    data = load_inventory()
    data = [row for row in data if not (
        row['item'].lower() == item.lower() and
        row['company'].lower() == company.lower() and
        row['model'].lower() == model.lower()
    )]
    save_inventory(data)

def record_sale(item, company, model, qty, price):
    qty = int(qty)
    price = float(price)
    # Deduct stock
    update_stock(item, company, model, qty, "subtract")
    # Save sale record
    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["datetime", "item", "company", "model", "quantity", "price"])
    with open(SALES_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), item, company, model, qty, price])
