import pdfplumber
import os
import re
from datetime import datetime
import dateparser

def clean_text(text):
    if not text: return ""
    text = text.replace('：', ':').replace('\xa0', ' ')
    # Merge hyphenated words across lines (e.g., "Con-\ntract" -> "Contract")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    return text

def find_amount_in_text(text):
    """Finds the largest number that looks like currency"""
    # Supports JPY format 10,025,000 and USD 10,000.00
    pattern = r"(?:[A-Z]{3}|[\$£€¥])?\s?([\d,]+\.?\d{0,2})"
    matches = re.findall(pattern, text)
    valid_amts = []
    for m in matches:
        try:
            val = float(re.sub(r'[^\d.]', '', m))
            if val > 0: valid_amts.append(val)
        except: pass
    return max(valid_amts) if valid_amts else 0.0

def find_amount_in_block(text_block):
    """(Alias for compatibility) Finds amount in a specific block"""
    return find_amount_in_text(text_block)

def extract_dynamic_date(text, default=None):
    # Matches 2025/12/05, 05-Dec-2025, 12th Jan 2025 etc.
    regex = r'(?:Date|Dated|On)?\s*[:.]?\s*(\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})'
    match = re.search(regex, text, re.IGNORECASE)
    if match:
        try:
            dt = dateparser.parse(match.group(1))
            if dt: return dt.date()
        except: pass
    return default or datetime.now().date()

def parse_multi_sow_agreement(pdf_path):
    """
    ROBUST PARSER: Scans for multiple 'Scope of Work' sections.
    """
    extracted_sows = []
    global_date = datetime.now().date()
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
            text = clean_text(full_text)
            
            # 1. Find Global Document Date
            global_date = extract_dynamic_date(text[:1000])

            # 2. ROBUST REGEX for SOW
            # Matches: "Scope of Work (SOW):" OR "Scope of Work:" OR "SOW" followed by newline
            # (?:\s*\(SOW\))?  --> Optional (SOW)
            # \s*[:\n]         --> Matches a Colon OR a New Line (The fix!)
            sow_pattern = re.compile(r"(?:Scope of Work|SOW)(?:\s*\(SOW\))?\s*[:\n]", re.IGNORECASE)
            
            matches = list(sow_pattern.finditer(text))
            
            if not matches:
                # Fallback: Treat whole doc as one SOW
                amt = find_amount_in_text(text)
                return [{'name': 'General Agreement', 'amount': amt, 'date': global_date}]

            # 3. Iterate matches
            for i, match in enumerate(matches):
                start_idx = match.start()
                end_idx = match.end()
                
                # A. Find Name (Look backwards)
                preceding_text = text[max(0, start_idx-200):start_idx]
                lines = [l.strip() for l in preceding_text.split('\n') if l.strip()]
                
                # The line immediately before "Scope of Work" is usually the Title
                sow_name = lines[-1] if lines else f"Project Section {i+1}"
                # Clean bullet points "1. Project..." -> "Project..."
                sow_name = re.sub(r'^[\d.\-\)]+\s*', '', sow_name) 

                # B. Find Content (Look forwards until next match)
                next_start = matches[i+1].start() if i+1 < len(matches) else len(text)
                block_text = text[end_idx:next_start]
                
                # C. Extract Data
                amount = find_amount_in_text(block_text)
                section_date = extract_dynamic_date(block_text, default=global_date)
                
                extracted_sows.append({
                    'name': sow_name,
                    'amount': amount,
                    'date': section_date
                })
                
    except Exception as e:
        print(f"Error parsing SOW: {e}")
        return []

    return extracted_sows

def parse_invoice_v2(pdf_path):
    """Advanced Invoice Parser with Table Support"""
    inv_data = {
        'no': "DRAFT", 
        'date': datetime.now().date(), 
        'total': 0.0,
        'items': [] 
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = clean_text(pdf.pages[0].extract_text())
            
            # Header Info
            no_match = re.search(r"(?:Invoice\s*No\.?|No\.?)\s*[:.]?\s*([A-Z0-9\-\/]{5,})", first_page_text, re.IGNORECASE)
            if no_match: inv_data['no'] = no_match.group(1).strip()
            
            inv_data['date'] = extract_dynamic_date(first_page_text)
            inv_data['total'] = find_amount_in_text(first_page_text)

            # Table Scan
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        cleaned_row = [clean_text(str(cell)) if cell else "" for cell in row]
                        
                        # Find Description & Amount columns
                        desc_candidates = [c for c in cleaned_row if len(c) > 5 and not re.match(r'^[\d,.]+$', c)]
                        amt_candidates = [c for c in cleaned_row if re.search(r'[\d,]+\.?\d*', c)]
                        
                        if desc_candidates and amt_candidates:
                            desc = desc_candidates[0].replace('\n', ' ')
                            if "Description" in desc or "Item" in desc: continue
                            
                            try:
                                amt_txt = amt_candidates[-1]
                                amt = float(re.sub(r'[^\d.]', '', amt_txt))
                                if amt > 0:
                                    inv_data['items'].append({'desc': desc, 'amount': amt})
                            except: pass

    except Exception as e:
        print(f"Error parsing PDF: {e}")

    if not inv_data['items']:
        inv_data['items'].append({'desc': 'General Services', 'amount': inv_data['total']})
        
    return inv_data

def parse_payment(pdf_path):
    """Simple Payment Parser"""
    inv_ref = None
    amt = 0.0
    p_date = datetime.now().date()
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = clean_text(pdf.pages[0].extract_text() or "")
            amt = find_amount_in_text(text)
            p_date = extract_dynamic_date(text)
            
            match = re.search(r"(INV-[A-Z0-9\-]+)", text)
            if match: inv_ref = match.group(1).strip()
    except: pass
    
    return inv_ref, amt, p_date