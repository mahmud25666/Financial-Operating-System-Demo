import pdfplumber
import os
import re
from datetime import datetime
import dateparser # Highly recommended to keep this import

def clean_text(text):
    text = text.replace('：', ':').replace('\xa0', ' ')
    return text

def find_amount_on_line(line):
    pattern = r"(?:[A-Z]{3}|[\$£€¥])?\s?([\d,]+\.?\d{2})"
    matches = re.findall(pattern, line)
    return matches[-1] if matches else None

def parse_invoice(pdf_path):
    filename = os.path.basename(pdf_path)
    
    # 1. SETUP DEFAULTS
    invoice_no = "MANUAL_CHECK"
    inv_date = datetime.now().date() 
    amount = 0.0
    project = "General Project"

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                raw_text = pdf.pages[0].extract_text()
            else:
                raw_text = ""

            if not raw_text:
                return invoice_no, inv_date, amount, project
                
            text = clean_text(raw_text)
            lines = text.split('\n')

            # --- 2. FIND INVOICE NUMBER ---
            inv_keywords = ["Invoice No", "Invoice Number", "Bill No", "Inv", "Reference"]
            found_inv = False
            for keyword in inv_keywords:
                search_regex = rf"(?i){keyword}[.:#\s]*([A-Z0-9\-\/]{{3,}}[\s\-]?[A-Z0-9\-\/]+)"
                match = re.search(search_regex, text)
                if match:
                    invoice_no = match.group(1).strip()
                    found_inv = True
                    break
            
            if not found_inv:
                fallback = re.search(r"(INV-[A-Z0-9\-\/]+)", text)
                if fallback: invoice_no = fallback.group(1)

            # --- 3. FIND AMOUNT ---
            amount_keywords = ["Grand Total", "Total Amount", "Balance Due", "Total"]
            amount_found = False
            
            for line in lines:
                for keyword in amount_keywords:
                    if keyword.lower() in line.lower():
                        raw_num = find_amount_on_line(line)
                        if raw_num:
                            try:
                                amount = float(re.sub(r'[^\d.]', '', raw_num))
                                amount_found = True
                            except: pass
                        if amount_found: break
                if amount_found: break
            
            if amount == 0.0:
                all_money = re.findall(r"[\d,]+\.\d{2}", text)
                if all_money:
                    try:
                        values = [float(re.sub(r'[^\d.]', '', x)) for x in all_money]
                        amount = max(values)
                    except: pass

            # --- 4. IMPROVED DATE FINDING ---
            # This updated regex catches:
            # 2025/11/30 | 2025-11-30 | 2025.11.30
            # 30/11/2025 | 30-11-2025 | 30 Nov 2025
            date_regex = r'(?:Date|Invoice Date|Dated)\s*[:.]?\s*(\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})'
            
            date_pattern = re.search(date_regex, text, re.IGNORECASE)
            
            if date_pattern:
                date_str = date_pattern.group(1)
                
                # OPTION A: Use dateparser (Best for versatility)
                # It automatically handles 2025/11/30 vs 30/11/2025 automatically
                try:
                    parsed_dt = dateparser.parse(date_str)
                    if parsed_dt:
                        inv_date = parsed_dt.date()
                except:
                    pass
                
                # OPTION B: Manual Fallback (If dateparser fails or isn't installed)
                # We added "%Y/%m/%d" specifically for your case
                if inv_date == datetime.now().date(): 
                    formats = [
                        "%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d", # Year First (2025/11/30)
                        "%d/%m/%Y", "%d-%m-%Y",               # Day First
                        "%B %d, %Y", "%b %d, %Y"              # Text (Nov 30, 2025)
                    ]
                    for fmt in formats:
                        try:
                            inv_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue

            # --- 5. FIND PROJECT ---
            if "bike" in filename.lower(): project = "EV Bike Rollout"
            elif "consulting" in filename.lower(): project = "Consulting"

    except Exception as e:
        print(f"Error reading PDF {filename}: {e}")

    return invoice_no, inv_date, amount, project