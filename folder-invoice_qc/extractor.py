import re
import pdfplumber
from datetime import datetime
from typing import Optional, Dict, Any
from .models import Invoice

def parse_german_float(value_str: str) -> float:
    if not value_str:
        return 0.0
    clean_str = value_str.replace('.', '').replace(',', '.')
    clean_str = re.sub(r'[^\d\.]', '', clean_str)
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def parse_german_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%d.%m.%Y")
        return dt.date()
    except ValueError:
        return None

def extract_invoice_from_pdf(pdf_path: str) -> Optional[Dict[str, Any]]:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            
            # 1. Basic Metadata
            inv_num_match = re.search(r'Bestellung\s+(AUFNR\d+)', text)
            invoice_number = inv_num_match.group(1) if inv_num_match else None

            date_match = re.search(r'vom\s+(\d{2}\.\d{2}\.\d{4})', text)
            invoice_date = parse_german_date(date_match.group(1)) if date_match else None

            # 2. Parties (Heuristics)
            lines = text.split('\n')
            seller_name = lines[3].strip() if len(lines) > 4 else None
            buyer_name = None
            try:
                kunden_idx = text.find("Kundenanschrift")
                if kunden_idx != -1:
                    sub_text = text[kunden_idx:].split('\n')
                    if len(sub_text) > 1:
                        buyer_name = sub_text[1].strip() 
            except:
                pass

            # 3. Totals
            net_match = re.search(r'Gesamtwert\s+\w+\s+([\d\.,]+)', text)
            tax_match = re.search(r'MwSt\..+EUR\s+([\d\.,]+)', text)
            gross_match = re.search(r'Gesamtwert inkl\. MwSt\.\s+EUR\s+([\d\.,]+)', text)

            net_val = parse_german_float(net_match.group(1)) if net_match else 0.0
            tax_val = parse_german_float(tax_match.group(1)) if tax_match else 0.0
            gross_val = parse_german_float(gross_match.group(1)) if gross_match else 0.0

            # 4. Line Items
            line_items = []
            tables = page.extract_table()
            if tables:
                for row in tables:
                    if not row or row[0] == 'Pos.' or row[0] is None:
                        continue
                    try:
                        desc = row[1].replace('\n', ' ')
                        unit_price = parse_german_float(row[2])
                        qty_str = row[3].split()[0]
                        qty = parse_german_float(qty_str)
                        line_total = parse_german_float(row[-1])

                        line_items.append({
                            "description": desc,
                            "quantity": qty,
                            "unit_price": unit_price,
                            "line_total": line_total
                        })
                    except (IndexError, ValueError):
                        continue

            return {
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "seller_name": seller_name,
                "buyer_name": buyer_name,
                "currency": "EUR",
                "totals": {
                    "net_amount": net_val,
                    "tax_amount": tax_val,
                    "gross_amount": gross_val
                },
                "line_items": line_items
            }
    except Exception as e:
        print(f"Error extracting {pdf_path}: {e}")
        return None
