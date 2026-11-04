import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import supermarket_core as core

class SupermarketApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛒 Smart Supermarket Inventory & Expiry Alert System")
        self.geometry("1060x720")
        self.configure(bg="#f8fafc")

        self.inventory = core.load_inventory()

        # Styles
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0")

        # Top Banner
        top_frame = tk.Frame(self, bg="#1e3a8a", height=60)
        top_frame.pack(fill=tk.X)
        tk.Label(top_frame, text="🏪 SMART SUPERMARKET INVENTORY SYSTEM", font=("Segoe UI", 14, "bold"), fg="white", bg="#1e3a8a").pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(top_frame, text=f"📅 {datetime.now().strftime('%d %B %Y')}", font=("Segoe UI", 11), fg="#93c5fd", bg="#1e3a8a").pack(side=tk.RIGHT, padx=20)

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="  📊 Dashboard & Alerts  ")
        self.notebook.add(self.tab2, text="  📋 Inventory Manager  ")
        self.notebook.add(self.tab3, text="  ➕ Stock In (Add Item)  ")
        self.notebook.add(self.tab4, text="  🛒 Cashier Billing Counter  ")

        self.build_dashboard()
        self.build_inventory()
        self.build_stock_in()
        self.build_billing()

        self.refresh_views()

    # 1. DASHBOARD
    def build_dashboard(self):
        cards = tk.Frame(self.tab1, bg="#f8fafc")
        cards.pack(fill=tk.X, pady=10)

        self.kpis = {}
        for title, col in [("Total Products", "#1e3a8a"), ("🔴 Expired", "#dc2626"), ("🟡 Near Expiry (30% OFF)", "#d97706"), ("🔵 Vendor Return", "#2563eb"), ("⚠️ Low Stock", "#7c3aed")]:
            f = tk.Frame(cards, bg="white", relief="solid", bd=1, highlightbackground=col, highlightthickness=2)
            f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
            tk.Label(f, text=title, font=("Segoe UI", 9, "bold"), fg="#64748b", bg="white").pack(pady=(8, 2))
            val = tk.Label(f, text="0", font=("Segoe UI", 18, "bold"), fg=col, bg="white")
            val.pack(pady=(0, 8))
            self.kpis[title] = val

        tk.Label(self.tab1, text="🔔 Actionable Live Alerts:", font=("Segoe UI", 11, "bold"), bg="#f8fafc").pack(anchor="w", padx=10, pady=(10, 4))
        cols = ("level", "id", "name", "rack", "stock", "expiry", "action")
        self.alert_tree = ttk.Treeview(self.tab1, columns=cols, show="headings", height=12)
        for c in cols:
            self.alert_tree.heading(c, text=c.capitalize())
        self.alert_tree.column("name", width=200)
        self.alert_tree.column("action", width=250)
        self.alert_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.alert_tree.tag_configure("EXPIRED", background="#fee2e2", foreground="#991b1b")
        self.alert_tree.tag_configure("NEAR_EXPIRY", background="#fef3c7", foreground="#92400e")
        self.alert_tree.tag_configure("VENDOR_RETURN", background="#dbeafe", foreground="#1e40af")

    # 2. INVENTORY TABLE
    def build_inventory(self):
        top = tk.Frame(self.tab2, bg="#f8fafc")
        top.pack(fill=tk.X, pady=8)
        tk.Label(top, text="🔍 Search:", font=("Segoe UI", 10, "bold"), bg="#f8fafc").pack(side=tk.LEFT, padx=10)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_inventory_table())
        ttk.Entry(top, textvariable=self.search_var, width=25).pack(side=tk.LEFT)

        cols = ("id", "name", "category", "batch", "rack", "qty", "price", "expiry", "status")
        self.inv_tree = ttk.Treeview(self.tab2, columns=cols, show="headings", height=15)
        for c in cols:
            self.inv_tree.heading(c, text=c.capitalize())
        self.inv_tree.column("name", width=220)
        self.inv_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.inv_tree.tag_configure("EXPIRED", background="#fee2e2")
        self.inv_tree.tag_configure("NEAR_EXPIRY", background="#fef3c7")
        self.inv_tree.tag_configure("SAFE", background="#f0fdf4")

    # 3. STOCK IN FORM
    def build_stock_in(self):
        card = tk.Frame(self.tab3, bg="white", relief="solid", bd=1)
        card.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        tk.Label(card, text="📦 Add New Product Batch", font=("Segoe UI", 13, "bold"), bg="white", fg="#1e3a8a").grid(row=0, column=0, columnspan=2, pady=15, padx=20, sticky="w")

        fields = ["Product ID:", "Product Name:", "Category:", "Batch Number:", "Rack No:", "Stock Quantity:", "Selling Price (₹):", "Expiry Date (YYYY-MM-DD):"]
        self.form_entries = {}
        for idx, f in enumerate(fields, start=1):
            tk.Label(card, text=f, font=("Segoe UI", 10, "bold"), bg="white").grid(row=idx, column=0, padx=20, pady=6, sticky="w")
            e = ttk.Entry(card, width=35)
            e.grid(row=idx, column=1, padx=10, pady=6, sticky="w")
            self.form_entries[f] = e

        btn = tk.Button(card, text="💾 Save to Inventory", font=("Segoe UI", 10, "bold"), bg="#16a34a", fg="white", padx=15, pady=6, command=self.save_product)
        btn.grid(row=9, column=1, pady=15, sticky="w")

    def save_product(self):
        data = {
            "id": self.form_entries["Product ID:"].get(),
            "name": self.form_entries["Product Name:"].get(),
            "category": self.form_entries["Category:"].get(),
            "batch_no": self.form_entries["Batch Number:"].get(),
            "rack_no": self.form_entries["Rack No:"].get(),
            "quantity": self.form_entries["Stock Quantity:"].get(),
            "price": self.form_entries["Selling Price (₹):"].get(),
            "expiry_date": self.form_entries["Expiry Date (YYYY-MM-DD):"].get(),
        }
        ok, msg = core.add_product(data, self.inventory)
        if ok:
            messagebox.showinfo("Success", msg)
            for e in self.form_entries.values():
                e.delete(0, tk.END)
            self.refresh_views()
            self.notebook.select(self.tab2)
        else:
            messagebox.showerror("Error", msg)

    # 4. BILLING COUNTER
    def build_billing(self):
        left = tk.Frame(self.tab4, bg="white", relief="solid", bd=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right = tk.Frame(self.tab4, bg="white", relief="solid", bd=1)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(left, text="🛒 Cashier Checkout", font=("Segoe UI", 12, "bold"), bg="white", fg="#1e3a8a").pack(padx=15, pady=10, anchor="w")
        tk.Label(left, text="Select Product:", font=("Segoe UI", 10, "bold"), bg="white").pack(padx=15, anchor="w")
        self.bill_combo = ttk.Combobox(left, state="readonly", width=38)
        self.bill_combo.pack(padx=15, pady=5, anchor="w")

        tk.Label(left, text="Quantity to Buy:", font=("Segoe UI", 10, "bold"), bg="white").pack(padx=15, pady=(10, 0), anchor="w")
        self.bill_qty = ttk.Entry(left, width=15)
        self.bill_qty.insert(0, "1")
        self.bill_qty.pack(padx=15, pady=5, anchor="w")

        tk.Button(left, text="💳 Process Sale", font=("Segoe UI", 10, "bold"), bg="#2563eb", fg="white", padx=15, pady=6, command=self.do_bill).pack(padx=15, pady=15, anchor="w")

        tk.Label(right, text="🧾 POS Receipt Preview", font=("Segoe UI", 12, "bold"), bg="white", fg="#1e3a8a").pack(padx=15, pady=10, anchor="w")
        self.receipt = tk.Text(right, font=("Courier New", 10), bg="#f8fafc")
        self.receipt.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    def do_bill(self):
        sel = self.bill_combo.get()
        if not sel:
            return
        p_id = sel.split(" - ")[0].strip()
        ok, msg, b = core.process_billing(p_id, self.bill_qty.get(), self.inventory)
        if not ok:
            messagebox.showerror("Denied", msg)
            return

        self.receipt.delete("1.0", tk.END)
        self.receipt.insert(tk.END, "========================================\n")
        self.receipt.insert(tk.END, "       SMART SUPERMARKET POS RECEIPT    \n")
        self.receipt.insert(tk.END, "========================================\n")
        self.receipt.insert(tk.END, f"Date: {b['time']}\n")
        self.receipt.insert(tk.END, f"Item: {b['name']} ({b['id']})\n")
        self.receipt.insert(tk.END, f"Qty : {b['qty']}\n")
        self.receipt.insert(tk.END, f"Price: ₹{b['unit_price']:.2f}\n")
        if b["discount_pct"] > 0:
            self.receipt.insert(tk.END, f"Discount: -{b['discount_pct']}% (Clearance Offer!)\n")
            self.receipt.insert(tk.END, f"Saved   : ₹{b['savings']:.2f} 🎉\n")
        self.receipt.insert(tk.END, "----------------------------------------\n")
        self.receipt.insert(tk.END, f"TOTAL   : ₹{b['total']:.2f}\n")
        self.receipt.insert(tk.END, "========================================\n")
        self.receipt.insert(tk.END, f"Remaining Shelf Stock: {b['remaining_stock']}\n")
        if b["low_stock_warning"]:
            self.receipt.insert(tk.END, "⚠️ WARNING: Stock is low (≤ 5)!\n")

        self.refresh_views()

    # REFRESH VIEWS
    def refresh_views(self):
        self.inventory = core.load_inventory()
        cat = core.get_categorized_inventory(self.inventory)

        self.kpis["Total Products"].config(text=str(len(self.inventory)))
        self.kpis["🔴 Expired"].config(text=str(len(cat["expired"])))
        self.kpis["🟡 Near Expiry (30% OFF)"].config(text=str(len(cat["near_expiry"])))
        self.kpis["🔵 Vendor Return"].config(text=str(len(cat["vendor_return"])))
        self.kpis["⚠️ Low Stock"].config(text=str(len(cat["low_stock"])))

        for r in self.alert_tree.get_children():
            self.alert_tree.delete(r)

        for i in cat["expired"]:
            self.alert_tree.insert("", tk.END, values=("🔴 Expired", i["id"], i["name"], i["rack_no"], i["quantity"], i["expiry_date"], "Remove immediately from shelf!"), tags=("EXPIRED",))
        for i in cat["near_expiry"]:
            self.alert_tree.insert("", tk.END, values=("🟡 Near Expiry", i["id"], i["name"], i["rack_no"], i["quantity"], i["expiry_date"], f"30% Clearance Discount (₹{i['offer_price']})"), tags=("NEAR_EXPIRY",))
        for i in cat["vendor_return"]:
            self.alert_tree.insert("", tk.END, values=("🔵 Return", i["id"], i["name"], i["rack_no"], i["quantity"], i["expiry_date"], "Return to distributor"), tags=("VENDOR_RETURN",))

        self.refresh_inventory_table()
        vals = [f"{i['id']} - {i['name']}" for i in self.inventory]
        self.bill_combo["values"] = vals
        if vals and not self.bill_combo.get():
            self.bill_combo.set(vals[0])

    def refresh_inventory_table(self):
        q = self.search_var.get().strip().lower()
        for r in self.inv_tree.get_children():
            self.inv_tree.delete(r)
        for i in self.inventory:
            if q and q not in i["name"].lower() and q not in i["id"].lower():
                continue
            st = core.get_product_status(i)
            self.inv_tree.insert("", tk.END, values=(i["id"], i["name"], i["category"], i["batch_no"], i["rack_no"], i["quantity"], f"₹{i['price']}", i["expiry_date"], st["status_label"]), tags=(st["status"],))

if __name__ == "__main__":
    app = SupermarketApp()
    app.mainloop()