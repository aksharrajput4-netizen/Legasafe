import pdfplumber
import re
from collections import defaultdict

SUBS_DB = {
    "NETFLIX": {"cat": "Entertainment", "price": 649}, "HOTSTAR": {"cat": "Entertainment", "price": 299},
    "SPOTIFY": {"cat": "Music", "price": 119}, "YOUTUBE": {"cat": "Video/Music", "price": 129},
    "ZOMATO": {"cat": "Food", "price": 199}, "SWIGGY": {"cat": "Food", "price": 249},
    "AMAZON": {"cat": "Shopping", "price": 179}, "LINKEDIN": {"cat": "Professional", "price": 1300}
}

INDIAN_KEYWORDS = {
    "Food & Dining": ["TIKI", "CHAAT", "ZOMATO", "SWIGGY", "BLINKIT", "MCDONALDS", "CAFE", "DAIRY", "RESTAURANT"],
    "Transport": ["UBER", "OLA", "RAPIDO", "AUTO", "METRO", "IRCTC", "PETROL", "CAB", "FLIGHT"],
    "Shopping": ["AMAZON", "FLIPKART", "MYNTRA", "CLOTH", "ELECTRONICS", "SHOES"],
    "Health & Medical": ["PHARMACY", "MEDICAL", "HOSPITAL", "CLINIC", "DOCTOR", "APOLLO"],
    "Bills & Utilities": ["ELECTRICITY", "POWER", "WATER", "WIFI", "AIRTEL", "JIO", "RECHARGE", "RENT"],
    "Investments": ["MUTUAL FUND", "SIP", "ZERODHA", "GROWW", "LIC", "FD"],
}

def clean_amount(val):
    if not val: return None
    cleaned = re.sub(r"[₹,\s]", "", str(val)).strip()
    try: return float(cleaned) if float(cleaned) > 0 else None
    except: return None

def categorize_transaction(description):
    desc_upper = description.upper()
    scores = defaultdict(int)
    for category, keywords in INDIAN_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_upper: scores[category] += len(kw.split())
    if not scores: return "Other"
    return max(scores, key=scores.get)

def process_pdf(pdf_file_object):
    transactions = []
    full_text = ""
    with pdfplumber.open(pdf_file_object) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: full_text += t + "\n"
            for table in (page.extract_tables() or []):
                for row in table:
                    if not row or len(row) < 4: continue
                    cells = [str(c).strip() if c else "" for c in row]
                    description = cells[1] if len(cells) >= 4 else ""
                    debit = clean_amount(cells[3]) if len(cells) >= 6 else clean_amount(cells[2]) if len(cells) >= 4 else None
                    if not description or not debit: continue
                    desc_upper = description.upper()
                    if any(skip in desc_upper for skip in ["TRF FROM", "SALARY", "INTEREST CREDIT", "REFUND"]): continue
                    if 1 <= debit <= 200000:
                        transactions.append({"description": description, "amount": debit, "category": categorize_transaction(description)})

    found_subs = []
    for keyword, info in SUBS_DB.items():
        if keyword.upper() in full_text.upper():
            found_subs.append({"name": keyword.title(), "cost": info["price"]})

    grand_total = sum(t["amount"] for t in transactions)
    cat_totals = defaultdict(float)
    for t in transactions: cat_totals[t["category"]] += t["amount"]

    return {
        "total_spent": grand_total, "transaction_count": len(transactions),
        "subscriptions_found": found_subs, "category_breakdown": dict(cat_totals)
    }
