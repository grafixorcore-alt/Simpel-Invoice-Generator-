"""
Simple Invoice Generator - Desktop App (Tkinter + ReportLab)

Save this file as `invoice_desktop_app.py` and run with Python 3.
Dependencies: reportlab, pillow
Install with: pip install reportlab pillow

Features:
- Add items (description, qty, unit price)
- Shows subtotal, discount (%), total
- Add company name, address and logo
- Save invoice as PDF

Notes:
- Place a logo image (PNG/JPG) or use the "Load Logo" button.
- Default currency can be changed in the CURRENCY variable.
"""

import os
import io
import math
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, Listbox, StringVar, END, filedialog, messagebox, Frame, ttk, Scrollbar
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# --- Config ---
CURRENCY = "USD"  # change to your currency symbol, e.g. "LKR" or "Rs"
DEFAULT_FILENAME_PREFIX = "invoice"
PAGE_WIDTH, PAGE_HEIGHT = A4

# --- Utility functions ---

def money(v):
    try:
        v = float(v)
    except Exception:
        v = 0.0
    return f"{v:,.2f} {CURRENCY}"

# --- PDF generation ---

def generate_pdf(output_path, company_info, logo_path, items, discount_percent, invoice_meta):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = PAGE_WIDTH, PAGE_HEIGHT

    # Margins
    left_margin = 20 * mm
    right_margin = width - 20 * mm
    top = height - 20 * mm

    # Draw logo if present
    logo_width_mm = 40 * mm
    logo_height_mm = 25 * mm
    if logo_path and os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            img_w, img_h = img.size
            aspect = img_h / img_w
            target_w = logo_width_mm
            target_h = logo_width_mm * aspect
            # fit inside limits
            if target_h > logo_height_mm:
                target_h = logo_height_mm
                target_w = logo_height_mm / aspect
            c.drawImage(logo_path, left_margin, top - target_h - 5 * mm, width=target_w, height=target_h, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print("Logo load error:", e)

    # Company info
    text_x = left_margin + logo_width_mm + 5 * mm
    text_y = top - 5 * mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(text_x, text_y, company_info.get("name", ""))
    c.setFont("Helvetica", 10)
    text_y -= 12
    for line in company_info.get("address_lines", []):
        c.drawString(text_x, text_y, line)
        text_y -= 11

    # Invoice meta (date, invoice number)
    meta_x = right_margin - 70 * mm
    meta_y = top - 5 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(meta_x, meta_y, f"Invoice")
    c.setFont("Helvetica", 9)
    meta_y -= 14
    c.drawString(meta_x, meta_y, f"Date: {invoice_meta.get('date')}")
    meta_y -= 11
    c.drawString(meta_x, meta_y, f"Invoice #: {invoice_meta.get('invoice_no')}")

    # Draw table header
    table_top = top - 55 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, table_top, "Description")
    c.drawString(left_margin + 95 * mm, table_top, "Qty")
    c.drawString(left_margin + 110 * mm, table_top, "Unit Price")
    c.drawString(left_margin + 140 * mm, table_top, "Total")

    # Draw items
    y = table_top - 10
    c.setFont("Helvetica", 9)
    subtotal = 0.0
    for it in items:
        desc = it.get("desc", "")
        qty = float(it.get("qty", 0))
        unit = float(it.get("unit", 0))
        total = qty * unit
        subtotal += total
        # wrap description if long
        max_chars = 50
        lines = [desc[i:i+max_chars] for i in range(0, len(desc), max_chars)] if desc else [""]
        for li, line in enumerate(lines):
            if li == 0:
                c.drawString(left_margin, y, line)
                c.drawRightString(left_margin + 120 * mm, y, str(qty))
                c.drawRightString(left_margin + 150 * mm, y, f"{unit:,.2f}")
                c.drawRightString(right_margin, y, f"{total:,.2f}")
            else:
                c.drawString(left_margin, y, line)
            y -= 11
            # page break if low
            if y < 40 * mm:
                c.showPage()
                y = height - 40 * mm
    
    # Totals
    y -= 8
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(left_margin + 150 * mm, y, "Subtotal:")
    c.drawRightString(right_margin, y, f"{subtotal:,.2f}")
    y -= 12
    discount_amount = subtotal * (discount_percent / 100.0)
    c.setFont("Helvetica", 10)
    c.drawRightString(left_margin + 150 * mm, y, f"Discount ({discount_percent}%):")
    c.drawRightString(right_margin, y, f"-{discount_amount:,.2f}")
    y -= 12
    total_due = subtotal - discount_amount
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(left_margin + 150 * mm, y, "Total Due:")
    c.drawRightString(right_margin, y, f"{total_due:,.2f}")

    # Footer / notes
    y -= 25
    c.setFont("Helvetica", 9)
    notes = company_info.get("notes", "")
    if notes:
        c.drawString(left_margin, y, "Notes:")
        y -= 12
        c.setFont("Helvetica", 8)
        for line in notes.split('\n'):
            c.drawString(left_margin, y, line)
            y -= 10

    c.showPage()
    c.save()

# --- GUI App ---

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        root.title("Simple Invoice Generator")
        root.geometry("820x600")

        # Data
        self.items = []
        self.logo_path = None

        # Company info frame
        ci_frame = Frame(root, pady=6)
        ci_frame.pack(fill='x')
        Label(ci_frame, text="Company Name:").grid(row=0, column=0, sticky='w')
        self.company_name_var = StringVar(value="Your Company")
        Entry(ci_frame, textvariable=self.company_name_var, width=40).grid(row=0, column=1, sticky='w')
        Label(ci_frame, text="Address (\n for new line):").grid(row=1, column=0, sticky='nw')
        self.company_addr_var = StringVar(value="123 Business St, City")
        Entry(ci_frame, textvariable=self.company_addr_var, width=60).grid(row=1, column=1, sticky='w')
        Button(ci_frame, text="Load Logo", command=self.load_logo).grid(row=0, column=2, padx=6)

        # Items frame
        items_frame = Frame(root, pady=6)
        items_frame.pack(fill='both', expand=True)

        Label(items_frame, text="Description").grid(row=0, column=0)
        Label(items_frame, text="Qty").grid(row=0, column=1)
        Label(items_frame, text="Unit Price").grid(row=0, column=2)

        self.desc_entry = Entry(items_frame, width=50)
        self.desc_entry.grid(row=1, column=0, padx=4, pady=4)
        self.qty_entry = Entry(items_frame, width=10)
        self.qty_entry.grid(row=1, column=1, padx=4, pady=4)
        self.unit_entry = Entry(items_frame, width=12)
        self.unit_entry.grid(row=1, column=2, padx=4, pady=4)

        Button(items_frame, text="Add Item", command=self.add_item).grid(row=1, column=3, padx=6)
        Button(items_frame, text="Remove Selected", command=self.remove_selected).grid(row=2, column=3, padx=6, pady=4)
        Button(items_frame, text="Clear Items", command=self.clear_items).grid(row=3, column=3, padx=6, pady=4)

        # Listbox for items with scrollbar
        list_frame = Frame(items_frame)
        list_frame.grid(row=2, column=0, columnspan=3, rowspan=6, sticky='nsew', padx=4)
        items_frame.grid_rowconfigure(2, weight=1)
        items_frame.grid_columnconfigure(0, weight=1)

        self.items_list = Listbox(list_frame)
        self.items_list.pack(side='left', fill='both', expand=True)
        sb = Scrollbar(list_frame, orient='vertical')
        sb.pack(side='right', fill='y')
        self.items_list.config(yscrollcommand=sb.set)
        sb.config(command=self.items_list.yview)

        # Totals / Discount
        totals_frame = Frame(root, pady=6)
        totals_frame.pack(fill='x')
        Label(totals_frame, text="Discount (%) :").grid(row=0, column=0, sticky='w')
        self.discount_var = StringVar(value="0")
        Entry(totals_frame, textvariable=self.discount_var, width=8).grid(row=0, column=1, sticky='w')

        Button(totals_frame, text="Calculate Totals", command=self.update_totals).grid(row=0, column=2, padx=6)

        Label(totals_frame, text="Subtotal:").grid(row=1, column=0, sticky='w')
        self.subtotal_lbl = Label(totals_frame, text=money(0))
        self.subtotal_lbl.grid(row=1, column=1, sticky='w')

        Label(totals_frame, text="Total Due:").grid(row=1, column=2, sticky='w')
        self.total_lbl = Label(totals_frame, text=money(0))
        self.total_lbl.grid(row=1, column=3, sticky='w')

        # Footer controls
        footer_frame = Frame(root, pady=8)
        footer_frame.pack(fill='x')
        Button(footer_frame, text="Generate PDF Invoice", command=self.generate_invoice_pdf).pack(side='left', padx=6)
        Button(footer_frame, text="Quit", command=root.quit).pack(side='right', padx=6)

    def load_logo(self):
        p = filedialog.askopenfilename(title="Select logo image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if p:
            self.logo_path = p
            messagebox.showinfo("Logo loaded", f"Logo loaded: {os.path.basename(p)}")

    def add_item(self):
        desc = self.desc_entry.get().strip()
        try:
            qty = float(self.qty_entry.get())
        except Exception:
            qty = 0
        try:
            unit = float(self.unit_entry.get())
        except Exception:
            unit = 0
        if not desc:
            messagebox.showwarning("Missing description", "Please enter an item description")
            return
        self.items.append({"desc": desc, "qty": qty, "unit": unit})
        self.items_list.insert(END, f"{desc} — {qty} × {unit:,.2f} = {qty*unit:,.2f}")
        self.desc_entry.delete(0, END)
        self.qty_entry.delete(0, END)
        self.unit_entry.delete(0, END)
        self.update_totals()

    def remove_selected(self):
        sel = self.items_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self.items_list.delete(idx)
        del self.items[idx]
        self.update_totals()

    def clear_items(self):
        if messagebox.askyesno("Confirm", "Clear all items?"):
            self.items = []
            self.items_list.delete(0, END)
            self.update_totals()

    def update_totals(self):
        subtotal = 0.0
        for it in self.items:
            subtotal += float(it.get('qty', 0)) * float(it.get('unit', 0))
        try:
            disc = float(self.discount_var.get())
        except Exception:
            disc = 0.0
        disc = max(0.0, disc)
        discount_amount = subtotal * (disc / 100.0)
        total = subtotal - discount_amount
        self.subtotal_lbl.config(text=money(subtotal))
        self.total_lbl.config(text=money(total))

    def generate_invoice_pdf(self):
        if not self.items:
            messagebox.showwarning("No items", "Add at least one item before generating invoice")
            return
        company = {
            "name": self.company_name_var.get(),
            "address_lines": [line.strip() for line in self.company_addr_var.get().split('\n') if line.strip()],
            "notes": "Thank you for your business!"
        }
        try:
            discount_percent = float(self.discount_var.get())
        except Exception:
            discount_percent = 0.0
        invoice_no = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        invoice_meta = {"date": datetime.now().strftime('%Y-%m-%d'), "invoice_no": invoice_no}

        # Ask where to save
        default_name = f"{DEFAULT_FILENAME_PREFIX}_{invoice_no}.pdf"
        save_path = filedialog.asksaveasfilename(defaultextension='.pdf', initialfile=default_name, filetypes=[('PDF files', '*.pdf')])
        if not save_path:
            return
        try:
            generate_pdf(save_path, company, self.logo_path, self.items, discount_percent, invoice_meta)
            messagebox.showinfo("Saved", f"Invoice saved to: {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")


if __name__ == '__main__':
    root = Tk()
    app = InvoiceApp(root)
    root.mainloop()
