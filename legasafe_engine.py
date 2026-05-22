%%writefile legasafe_engine.py
import io
import re
from collections import defaultdict
from datetime import datetime
import pdfplumber

def process_pdf(file):
    # ════════════════════════════════════════════════════════════
    #  DATABASES
    # ════════════════════════════════════════════════════════════

      ANNUAL_KEYWORDS = [
      "ANNUAL", "YEARLY", "1 YEAR", "ONE YEAR",
      "12 MONTH", "12MONTH", "365", "1YR",
      "YEAR PLAN", "ANNUAL PLAN", "YEARLY PLAN", "PER YEAR",
  ]

  MONTH_MAP = {
      "01": "Jan", "02": "Feb", "03": "Mar",
      "04": "Apr", "05": "May", "06": "Jun",
      "07": "Jul", "08": "Aug", "09": "Sep",
      "10": "Oct", "11": "Nov", "12": "Dec",
  }

  SUBS_DB = {
      "NETFLIX":             {"cat": "Entertainment 🎬", "price": 649},
      "HOTSTAR":             {"cat": "Entertainment 🎬", "price": 299},
      "DISNEY":              {"cat": "Entertainment 🎬", "price": 299},
      "SONYLIV":             {"cat": "Entertainment 🎬", "price": 299},
      "ZEE5":                {"cat": "Entertainment 🎬", "price": 99},
      "VOOT":                {"cat": "Entertainment 🎬", "price": 99},
      "JIOCINEMA":           {"cat": "Entertainment 🎬", "price": 99},
      "MXPLAYER":            {"cat": "Entertainment 🎬", "price": 99},
      "ALTBALAJI":           {"cat": "Entertainment 🎬", "price": 100},
      "TATAPLAY":            {"cat": "Entertainment 🎬", "price": 200},
      "DISCOVERY":           {"cat": "Entertainment 🎬", "price": 299},
      "EROSNOW":             {"cat": "Entertainment 🎬", "price": 99},
      "SPOTIFY":             {"cat": "Music 🎵",         "price": 119},
      "JIOSAAVN":            {"cat": "Music 🎵",         "price": 99},
      "GAANA":               {"cat": "Music 🎵",         "price": 99},
      "WYNK":                {"cat": "Music 🎵",         "price": 99},
      "APPLE MUSIC":         {"cat": "Music 🎵",         "price": 99},
      "YOUTUBE MUSIC":       {"cat": "Music 🎵",         "price": 99},
      "YOUTUBE PREMIUM":     {"cat": "Video/Music 🎵",   "price": 129},
      "YOUTUBE":             {"cat": "Video/Music 🎵",   "price": 129},
      "ZOMATO":              {"cat": "Food 🍕",          "price": 199},
      "SWIGGY":              {"cat": "Food 🍕",          "price": 249},
      "BLINKIT":             {"cat": "Food 🍕",          "price": 99},
      "ZEPTO":               {"cat": "Food 🍕",          "price": 99},
      "BIGBASKET":           {"cat": "Food 🍕",          "price": 99},
      "CUREFIT":             {"cat": "Health 💪",        "price": 800},
      "HEALTHIFYME":         {"cat": "Health 💪",        "price": 400},
      "PRACTO":              {"cat": "Health 💪",        "price": 299},
      "ICLOUD":              {"cat": "Storage ☁️",       "price": 75},
      "GOOGLE ONE":          {"cat": "Storage ☁️",       "price": 130},
      "GOOGLE PLAY":         {"cat": "Apps 📱",          "price": 0},
      "DROPBOX":             {"cat": "Storage ☁️",       "price": 800},
      "MICROSOFT":           {"cat": "Productivity 💼",  "price": 420},
      "OFFICE 365":          {"cat": "Productivity 💼",  "price": 420},
      "ADOBE":               {"cat": "Design 🎨",        "price": 1675},
      "CANVA":               {"cat": "Design 🎨",        "price": 400},
      "NOTION":              {"cat": "Productivity 💼",  "price": 400},
      "GRAMMARLY":           {"cat": "Productivity 💼",  "price": 900},
      "LINKEDIN":            {"cat": "Professional 💼",  "price": 1300},
      "ZOOM":                {"cat": "Communication 💬", "price": 1300},
      "AUDIBLE":             {"cat": "Books 📚",         "price": 199},
      "KINDLE":              {"cat": "Books 📚",         "price": 169},
      "BYJU":                {"cat": "Education 📖",     "price": 2000},
      "UNACADEMY":           {"cat": "Education 📖",     "price": 1500},
      "VEDANTU":             {"cat": "Education 📖",     "price": 1000},
      "COURSERA":            {"cat": "Education 📖",     "price": 2500},
      "AIRTEL":              {"cat": "Telecom 📱",       "price": 299},
      "VODAFONE":            {"cat": "Telecom 📱",       "price": 299},
      "BSNL":                {"cat": "Telecom 📱",       "price": 199},
      "JIO":                 {"cat": "Telecom 📱",       "price": 239},
      "TINDER":              {"cat": "Social ❤️",        "price": 400},
      "BUMBLE":              {"cat": "Social ❤️",        "price": 400},
      "AMAZON PRIME":        {"cat": "Shopping 🛍️",      "price": 299},
      "AMAZON":              {"cat": "Shopping 🛍️",      "price": 179},
      "FLIPKART":            {"cat": "Shopping 🛍️",      "price": 499},
      "TIMES PRIME":         {"cat": "Bundle ⭐",        "price": 999},
      "XBOX":                {"cat": "Gaming 🎮",        "price": 499},
      "PLAYSTATION":         {"cat": "Gaming 🎮",        "price": 499},
      "PLAYSTATION NETWORK": {"cat": "Gaming 🎮",        "price": 499},
      "STEAM":               {"cat": "Gaming 🎮",        "price": 350},
      "EPIC GAMES":          {"cat": "Gaming 🎮",        "price": 0},
  }
    INDIAN_KEYWORDS = {
      "🍕 Food & Dining": [
          "TIKI", "TIKKI", "CHAAT", "PANI PURI", "PANIPURI",
          "BHELPURI", "VADA PAV", "SAMOSA", "DHABA", "BIRYANI",
          "HALWAI", "MITHAI", "SWEETS", "BAKERY", "CAFE",
          "CANTEEN", "RESTAURANT", "FOOD", "JUICE", "LASSI",
          "CHAI", "TEA", "COFFEE", "SNACKS", "TIFFIN", "MESS",
          "PIZZA", "BURGER", "NOODLES", "ROLL", "KIRANA",
          "GROCERY", "VEGETABLES", "SABZI", "FRUITS", "MART",
          "ZOMATO", "SWIGGY", "BLINKIT", "ZEPTO", "BIGBASKET",
          "MCDONALDS", "STARBUCKS", "KFC", "DOMINOS", "SUBWAY",
          "TAPRI", "EVENING SNACKS",
      ],
      "🚗 Transport": [
          "UBER", "OLA", "RAPIDO", "AUTO", "CAB", "TAXI",
          "PETROL", "DIESEL", "FUEL", "PUMP", "BPCL", "IOCL",
          "INDIAN OIL", "CNG", "IRCTC", "RAILWAY", "TRAIN",
          "BUS", "METRO", "METRO CARD", "FASTAG", "TOLL",
          "PARKING", "REDBUS", "IXIGO",
      ],
      "🛍️ Shopping": [
          "AMAZON", "FLIPKART", "MYNTRA", "AJIO", "MEESHO",
          "NYKAA", "MALL", "CLOTH", "GARMENTS", "FASHION",
          "FOOTWEAR", "SHOES", "ELECTRONICS", "MOBILE",
          "LAPTOP", "GIFT", "STATIONERY",
      ],
      "💊 Health & Medical": [
          "PHARMACY", "MEDICAL", "MEDICALS", "MEDICINE",
          "HOSPITAL", "CLINIC", "DOCTOR", "APOLLO", "MEDPLUS",
          "NETMEDS", "PHARMEASY", "1MG", "CHEMIST",
          "DIAGNOSTIC", "LAB", "PATHOLOGY", "DENTAL",
          "HEALTHCARE", "DR.", "MAX HEALTHCARE",
          "DR LAL", "PATHLABS",
      ],
      "📚 Education": [
          "BYJU", "UNACADEMY", "VEDANTU", "SCHOOL", "COLLEGE",
          "FEES", "TUITION", "COACHING", "CLASSES", "ACADEMY",
          "INSTITUTE", "COURSE", "BOOKS", "LIBRARY", "EXAM",
      ],
      "💸 EMI & Loans": [
          "EMI", "LOAN", "FINANCE", "LENDING", "CREDIT",
          "BAJAJ", "REPAYMENT", "INTEREST", "INSTALMENT",
      ],
      "🏠 Bills & Utilities": [
          "ELECTRICITY", "BIJLI", "POWER", "WATER", "GAS",
          "LPG", "INDANE", "WIFI", "BROADBAND", "FIBER",
          "AIRTEL", "BSNL", "JIO", "VODAFONE", "DTH",
          "RECHARGE", "POSTPAID", "MAINTENANCE", "RENT",
          "SOCIETY", "METRO CARD",
      ],
      "💰 Investments": [
          "MUTUAL FUND", "SIP", "ZERODHA", "GROWW", "UPSTOX",
          "ANGEL", "SHARES", "STOCK", "GOLD", "FD", "RD",
          "LIC", "INSURANCE", "PPF", "NPS",
      ],
      "🎮 Gaming & Entertainment": [
          "NETFLIX", "HOTSTAR", "SPOTIFY", "YOUTUBE",
          "BOOKMYSHOW", "PVR", "INOX", "CINEMA", "MOVIE",
          "PLAYSTATION", "XBOX", "STEAM", "EPIC GAMES",
          "GAMING", "GAME STORE", "PLAYSTATION NETWORK",
      ],
      "✈️ Travel & Hotels": [
          "OYO", "AIRBNB", "TREEBO", "FLIGHT", "INDIGO",
          "AIRINDIA", "SPICEJET", "HOLIDAY", "TOUR", "RESORT",
          "GOIBIBO", "MAKEMYTRIP", "HOTEL ADVANCE",
      ],
      "💈 Personal Care": [
          "SALON", "SALOON", "BARBER", "PARLOUR", "SPA",
          "MASSAGE", "BEAUTY", "GROOMING", "HAIR", "NAILS",
      ],
  }
   UNNECESSARY = [
      "🍕 Food & Dining", "🛍️ Shopping",
      "🎮 Gaming & Entertainment", "✈️ Travel & Hotels",
      "💈 Personal Care",
   ]
  NECESSARY = [
      "💊 Health & Medical", "📚 Education",
      "💸 EMI & Loans", "🏠 Bills & Utilities", "💰 Investments",
  ]

   DEFAULT_BUDGETS = {
      "🍕 Food & Dining":          2000,
      "🚗 Transport":              1000,
      "🛍️ Shopping":               1500,
      "💊 Health & Medical":       1500,
      "📚 Education":              2000,
      "💸 EMI & Loans":            5000,
      "🏠 Bills & Utilities":      2000,
      "💰 Investments":            3000,
      "🎮 Gaming & Entertainment": 1000,
      "✈️ Travel & Hotels":        2000,
      "💈 Personal Care":           500,
  }

    # ════════════════════════════════════════════════════════════
    #  HELPER FUNCTIONS
    # ════════════════════════════════════════════════════════════

    def clean_amount(val):
        if not val:
            return None
        cleaned = re.sub(r"[₹,\s]", "", str(val)).strip()
        try:
            f = float(cleaned)
            return f if f > 0 else None
        except:
            return None

    def is_annual_desc(description):
        return any(kw in description.upper() for kw in ANNUAL_KEYWORDS)

    def extract_month(text):
        if not text:
            return None
        m = re.search(r"\b(\d{2})[/-](\d{2})[/-](\d{4})\b", text)
        if m:
            return MONTH_MAP.get(m.group(2))
        return None

    def smart_categorise(description):
        desc_upper = description.upper()
        scores     = defaultdict(int)
        for category, keywords in INDIAN_KEYWORDS.items():
            for kw in keywords:
                if kw in desc_upper:
                    scores[category] += len(kw.split())
        if not scores:
            return "❓ Unknown / Other", 0
        best = max(scores, key=scores.get)
        return best, min(scores[best] * 25, 100)

    # ════════════════════════════════════════════════════════════
    #  PDF READER ENGINE
    # ════════════════════════════════════════════════════════════
    
    transactions  = []
    full_text     = ""
    current_month = None

    try:
        # Check for password lock
        try:
            with pdfplumber.open(file) as t:
                t.pages[0].extract_text()
            password_needed = False
        except Exception:
            return None # Safely eject if PDF is locked

        with pdfplumber.open(file) as pdf:
            pages = len(pdf.pages)
            desc_idx = -1
            debit_idx = -1

            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    full_text += t + "\n"
                for table in (page.extract_tables() or []):
                    for row in table:
                        if not row or len(row) < 4:
                            continue

                        cells  = [str(c).strip() if c else "" for c in row]
                        joined = " ".join(cells).upper()

                        if any(h in joined for h in ["DATE", "DESCRIPTION", "DEBIT"]) and len(joined) < 200:
                            for i, cell in enumerate(cells):
                                cell_up = cell.upper()
                                if any(x in cell_up for x in ["DESC", "PARTICULARS"]):
                                    desc_idx = i
                                if any(x in cell_up for x in ["DEBIT", "AMOUNT"]):
                                    debit_idx = i
                            continue 

                        month_from_row = extract_month(cells[0])
                        if month_from_row:
                            current_month = month_from_row

                        description = ""
                        debit       = None

                        if desc_idx != -1 and debit_idx != -1 and len(cells) > max(desc_idx, debit_idx):
                            description = cells[desc_idx]
                            debit       = clean_amount(cells[debit_idx])
                        elif len(cells) >= 6:
                            description = cells[1]
                            debit       = clean_amount(cells[3])

                        if not description or not debit:
                            continue

                        desc_upper = description.upper()
                        if any(skip in desc_upper for skip in ["TRF FROM", "SALARY", "REFUND", "CASHBACK"]):
                            continue

                        if 1 <= debit <= 200000:
                            transactions.append({
                                "description": description,
                                "debit":       debit,
                                "is_annual":   is_annual_desc(description),
                                "month":       current_month or "Unknown",
                            })
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

    # ── Calculations ───────────────────────────────────────
    budgets = DEFAULT_BUDGETS.copy()

    found_subs = []
    seen       = set()
    for keyword, info in SUBS_DB.items():
        keyword_upper = keyword.upper()
        matched_txn   = None
        for txn in transactions:
            if keyword_upper in txn["description"].upper():
                matched_txn = txn
                break
        if not matched_txn and keyword_upper not in full_text.upper():
            continue
        key = keyword.split()[0]
        if key in seen:
            continue
        seen.add(key)
        
        base_price = info["price"]
        found_subs.append({
            "name":          keyword.title(),
            "amount":        base_price,
        })

    categorised   = defaultdict(list)
    for txn in transactions:
        cat, conf = smart_categorise(txn["description"])
        categorised[cat].append(txn)

    grand_total = sum(t["debit"] for txns in categorised.values() for t in txns)
    
    # Calculate a simplified Health Score for the frontend
    health_score = 85 if grand_total < 50000 else 60 if grand_total < 100000 else 40

    # ════════════════════════════════════════════════════════════
    #  THE FINAL HANDOFF (Sends data back to Streamlit)
    # ════════════════════════════════════════════════════════════
    return {
        "total_spent": grand_total,
        "transaction_count": len(transactions),
        "subscriptions_found": found_subs,
        "health_score": health_score
    }
# ════════════════════════════════════════════════════════════
    #  THE FINAL HANDOFF (Sends data back to app.py)
    # ════════════════════════════════════════════════════════════
    # Failsafe health score calculation just in case it's missing above
    health_score = 85 if grand_total < 50000 else 60 if grand_total < 100000 else 40

    return {
        "total_spent": grand_total,
        "transaction_count": len(transactions),
        "subscriptions_found": found_subs,
        "health_score": health_score
    }
