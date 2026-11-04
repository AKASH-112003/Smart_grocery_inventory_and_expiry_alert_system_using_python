import json
import os
from datetime import datetime

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")

def load_inventory(filepath=DEFAULT_DATA_FILE):
    """JSON ஃபைலில் இருந்து டேட்டாவை லோட் செய்யும்"""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []
    return []

def save_inventory(inventory, filepath=DEFAULT_DATA_FILE):
    """இன்வென்டரி டேட்டாவை ஃபைலில் சேமிக்கும்"""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(inventory, file, indent=4, ensure_ascii=False)

def parse_date(date_str):
    return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()

def add_product(product_data, inventory, filepath=DEFAULT_DATA_FILE):
    """புதிய பொருளை இன்வென்டரியில் சேர்க்கும்"""
    p_id = str(product_data.get("id", "")).strip().upper()
    name = str(product_data.get("name", "")).strip()
    category = str(product_data.get("category", "")).strip() or "General"
    batch_no = str(product_data.get("batch_no", "")).strip() or "N/A"
    rack_no = str(product_data.get("rack_no", "")).strip() or "Shelf"

    if not p_id or not name:
        return False, "Product ID and Name are unavailable."

    for item in inventory:
        if item["id"] == p_id:
            return False, f"Product ID '{p_id}' already exists."

    try:
        qty = int(product_data["quantity"])
        price = float(product_data["price"])
        expiry_str = str(product_data.get("expiry_date", "")).strip()
        parse_date(expiry_str)
    except Exception:
        return False, "Wrong Input! Date format YYYY-MM-DD format required."

    new_item = {
        "id": p_id,
        "name": name,
        "category": category,
        "batch_no": batch_no,
        "rack_no": rack_no,
        "quantity": qty,
        "price": round(price, 2),
        "expiry_date": expiry_str
    }
    inventory.append(new_item)
    save_inventory(inventory, filepath)
    return True, f"'{name}' added on "

def get_product_status(item, reference_date=None):
    """எக்ஸ்பயரி நிலையை கணக்கிடும் Core Logic"""
    if reference_date is None:
        reference_date = datetime.now().date()

    try:
        exp_date = parse_date(item["expiry_date"])
    except Exception:
        return {"days_left": 0, "status": "UNKNOWN", "status_label": "Unknown", "discount_pct": 0, "offer_price": item.get("price", 0.0)}

    days_left = (exp_date - reference_date).days
    orig_price = float(item.get("price", 0.0))

    if days_left < 0:
        return {
            "days_left": days_left,
            "status": "EXPIRED",
            "status_label": f"Expired ({abs(days_left)}d ago)",
            "discount_pct": 0,
            "offer_price": 0.0,
            "badge_color": "#dc2626"
        }
    elif 0 <= days_left <= 5:
        offer_price = round(orig_price * 0.70, 2)  # 30% Discount
        return {
            "days_left": days_left,
            "status": "NEAR_EXPIRY",
            "status_label": f"Expiring in {days_left}d (30% OFF)",
            "discount_pct": 30,
            "offer_price": offer_price,
            "badge_color": "#d97706"
        }
    elif 6 <= days_left <= 15:
        return {
            "days_left": days_left,
            "status": "VENDOR_RETURN",
            "status_label": f"Vendor Return ({days_left}d left)",
            "discount_pct": 0,
            "offer_price": orig_price,
            "badge_color": "#2563eb"
        }
    else:
        return {
            "days_left": days_left,
            "status": "SAFE",
            "status_label": f"Fresh ({days_left}d left)",
            "discount_pct": 0,
            "offer_price": orig_price,
            "badge_color": "#16a34a"
        }

def get_categorized_inventory(inventory, reference_date=None):
    summary = {"expired": [], "near_expiry": [], "vendor_return": [], "safe": [], "low_stock": []}
    for item in inventory:
        st = get_product_status(item, reference_date)
        enriched = {**item, **st}
        if st["status"] == "EXPIRED":
            summary["expired"].append(enriched)
        elif st["status"] == "NEAR_EXPIRY":
            summary["near_expiry"].append(enriched)
        elif st["status"] == "VENDOR_RETURN":
            summary["vendor_return"].append(enriched)
        else:
            summary["safe"].append(enriched)

        if int(item.get("quantity", 0)) <= 5:
            summary["low_stock"].append(enriched)
    return summary

def process_billing(p_id, quantity, inventory, reference_date=None, filepath=DEFAULT_DATA_FILE):
    """பில்லிங் செய்து ஸ்டாக்கை கழிக்கும் பங்க்ஷன்"""
    p_id = str(p_id).strip().upper()
    product = next((item for item in inventory if item["id"] == p_id), None)
    if not product:
        return False, f"Product ID '{p_id}' not found.", None

    status_info = get_product_status(product, reference_date)

    # 1. எக்ஸ்பயரி பொருளை விற்கவிடாமல் தடுக்கும் Guard
    if status_info["status"] == "EXPIRED":
        return False, f"🛑 SALE BLOCKED! '{product['name']}' EXPIRED , can't sale", None

    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "quantity must be greater than 0.", None
    except Exception:
        return False, "wrong quantity!", None

    if qty > product["quantity"]:
        return False, f"stock not available: {product['quantity']}", None

    unit_price = status_info["offer_price"]
    total = round(qty * unit_price, 2)
    savings = round(qty * (float(product["price"]) - unit_price), 2)

    product["quantity"] -= qty
    save_inventory(inventory, filepath)

    bill_data = {
        "id": product["id"],
        "name": product["name"],
        "rack": product["rack_no"],
        "qty": qty,
        "unit_price": float(product["price"]),
        "final_price": unit_price,
        "discount_pct": status_info["discount_pct"],
        "total": total,
        "savings": savings,
        "remaining_stock": product["quantity"],
        "low_stock_warning": product["quantity"] <= 5,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return True, "Bill generate successfully", bill_data