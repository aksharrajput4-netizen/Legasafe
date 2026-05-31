import io
import re
from collections import defaultdict
from datetime import datetime
import pdfplumber

# ════════════════════════════════════════════════════════════
#  DATABASES
# ════════════════════════════════════════════════════════════

CANCELLATION_URLS = {
    "NETFLIX": "netflix.com/cancelplan",
    "SPOTIFY": "spotify.com/account",
    "AMAZON PRIME": "amazon.in/primecentral",
    "HOTSTAR": "hotstar.com/account",
    "ZOMATO": "zomato.com/subscription",
    "SWIGGY": "swiggy.com/membership",
    "YOUTUBE PREMIUM": "youtube.com/paid_memberships",
    "GOOGLE PLAY": "play.google.com/store/account/subscriptions"
}

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
    "NETFLIX":             {"cat": "Entertainment", "price": 649},
    "HOTSTAR":             {"cat": "Entertainment", "price": 299},
    "DISNEY":              {"cat": "Entertainment", "price": 299},
    "SONYLIV":             {"cat": "Entertainment", "price": 299},
    "ZEE5":                {"cat": "Entertainment", "price": 99},
    "VOOT":                {"cat": "Entertainment", "price": 99},
    "JIOCINEMA":           {"cat": "Entertainment", "price": 99},
    "MXPLAYER":            {"cat": "Entertainment", "price": 99},
    "ALTBALAJI":           {"cat": "Entertainment", "price": 100},
    "TATAPLAY":            {"cat": "Entertainment", "price": 200},
    "DISCOVERY":           {"cat": "Entertainment", "price": 299},
    "EROSNOW":             {"cat": "Entertainment", "price": 99},
    "SPOTIFY":             {"cat": "Music",         "price": 119},
    "JIOSAAVN":            {"cat": "Music",         "price": 99},
    "GAANA":               {"cat": "Music",         "price": 99},
    "WYNK":                {"cat": "Music",         "price": 99},
    "APPLE MUSIC":         {"cat": "Music",         "price": 99},
    "YOUTUBE MUSIC":       {"cat": "Music",         "price": 99},
    "YOUTUBE PREMIUM":     {"cat": "Video/Music",   "price": 129},
    "YOUTUBE":             {"cat": "Video/Music",   "price": 129},
    "ZOMATO":              {"cat": "Food",          "price": 199},
    "SWIGGY":              {"cat": "Food",          "price": 249},
    "BLINKIT":             {"cat": "Food",          "price": 99},
    "ZEPTO":               {"cat": "Food",          "price": 99},
    "BIGBASKET":           {"cat": "Food",          "price": 99},
    "CUREFIT":             {"cat": "Health",        "price": 800},
    "HEALTHIFYME":         {"cat": "Health",        "price": 400},
    "PRACTO":              {"cat": "Health",        "price": 299},
    "ICLOUD":              {"cat": "Storage",       "price": 75},
    "GOOGLE ONE":          {"cat": "Storage",       "price": 130},
    # Fixed: Google Play has variable amounts so price=1
    # to avoid ratio issues
    "GOOGLE PLAY":         {"cat": "Apps",          "price": 1},
    "DROPBOX":             {"cat": "Storage",       "price": 800},
    "MICROSOFT":           {"cat": "Productivity",  "price": 420},
    "OFFICE 365":          {"cat": "Productivity",  "price": 420},
    "ADOBE":               {"cat": "Design",        "price": 1675},
    "CANVA":               {"cat": "Design",        "price": 400},
    "NOTION":              {"cat": "Productivity",  "price": 400},
    "GRAMMARLY":           {"cat": "Productivity",  "price": 900},
    "LINKEDIN":            {"cat": "Professional",  "price": 1300},
    "ZOOM":                {"cat": "Communication", "price": 1300},
    "AUDIBLE":             {"cat": "Books",         "price": 199},
    "KINDLE":              {"cat": "Books",         "price": 169},
    "BYJU":                {"cat": "Education",     "price": 2000},
    "UNACADEMY":           {"cat": "Education",     "price": 1500},
    "VEDANTU":             {"cat": "Education",     "price": 1000},
    "COURSERA":            {"cat": "Education",     "price": 2500},
    "AIRTEL":              {"cat": "Telecom",       "price": 299},
    "VODAFONE":            {"cat": "Telecom",       "price": 299},
    "BSNL":                {"cat": "Telecom",       "price": 199},
    "JIO":                 {"cat": "Telecom",       "price": 239},
    "TINDER":              {"cat": "Social",        "price": 400},
    "BUMBLE":              {"cat": "Social",        "price": 400},
    "AMAZON PRIME":        {"cat": "Shopping",      "price": 299},
    "AMAZON":              {"cat": "Shopping",      "price": 179},
    "FLIPKART":            {"cat": "Shopping",      "price": 499},
    "TIMES PRIME":         {"cat": "Bundle",        "price": 999},
    "XBOX":                {"cat": "Gaming",        "price": 499},
    "PLAYSTATION NETWORK": {"cat": "Gaming",        "price": 499},
    "PLAYSTATION":         {"cat": "Gaming",        "price": 499},
    "STEAM":               {"cat": "Gaming",        "price": 350},
    # Fixed: Epic Games has variable amounts so price=1
    "EPIC GAMES":          {"cat": "Gaming",        "price": 1},
    "PHYSICSWALLAH":   {"cat": "Education", "price": 999},
    "PW APP":          {"cat": "Education", "price": 999},
    "KUKU FM":         {"cat": "Entertainment", "price": 199},
    "POCKET FM":       {"cat": "Entertainment", "price": 199},
    "HOICHOI":         {"cat": "Entertainment", "price": 299},
    "SUN NXT":         {"cat": "Entertainment", "price": 99},
    "HUNGAMA":         {"cat": "Entertainment", "price": 99},
    "LIONSGATE":       {"cat": "Entertainment", "price": 99},
    "MANORAMA MAX":    {"cat": "Entertainment", "price": 99},
    "STAGE OTT":       {"cat": "Entertainment", "price": 99}
}

COMPILED_SUBS_PATTERNS = {
    keyword: re.compile(r"\b" + re.escape(keyword) + r"\b")
    for keyword in SUBS_DB
}

# ════════════════════════════════════════════════════════════
#  FIX 1 — WORD BOUNDARY KEYWORDS
#  LAB won't match MALABAR
#  GAS won't match VEGAS
#  RECHARGE now correctly detected
# ════════════════════════════════════════════════════════════

INDIAN_KEYWORDS = {
    "Food & Dining": [
        r"\bTIKI\b", r"\bTIKKI\b", r"\bCHAAT\b",
        r"\bPANI PURI\b", r"\bPANIPURI\b",
        r"\bSAMOSA\b", r"\bDHABA\b", r"\bBIRYANI\b",
        r"\bHALWAI\b", r"\bMITHAI\b", r"\bSWEETS\b",
        r"\bBAKERY\b", r"\bCAFE\b", r"\bCANTEEN\b",
        r"\bRESTAURANT\b", r"\bJUICE\b", r"\bLASSI\b",
        r"\bCHAI\b", r"\bSNACKS\b", r"\bTIFFIN\b",
        r"\bPIZZA\b", r"\bBURGER\b", r"\bNOODLES\b",
        r"\bKIRANA\b", r"\bGROCERY\b", r"\bSABZI\b",
        r"\bFRUITS\b", r"\bZOMATO\b", r"\bSWIGGY\b",
        r"\bBLINKIT\b", r"\bZEPTO\b", r"\bBIGBASKET\b",
        r"\bMCDONALDS\b", r"\bSTARBUCKS\b", r"\bKFC\b",
        r"\bDOMINOS\b", r"\bSUBWAY\b", r"\bTAPRI\b",
        r"\bFOOD\b", r"\bMEALS\b", r"\bHOTEL\b",
    ],
    "Transport": [
        r"\bUBER\b", r"\bOLA\b", r"\bRAPIDA\b",
        r"\bAUTO\b", r"\bCAB\b", r"\bTAXI\b",
        r"\bPETROL\b", r"\bDIESEL\b", r"\bFUEL\b",
        r"\bBPCL\b", r"\bIOCL\b", r"\bINDIAN OIL\b",
        r"\bCNG\b", r"\bIRCTC\b", r"\bRAILWAY\b",
        r"\bTRAIN\b", r"\bMETRO\b", r"\bFASTAG\b",
        r"\bTOLL\b", r"\bPARKING\b", r"\bREDBUS\b",
        r"\bIXIGO\b", r"\bTRAVELS\b",
        r"\bMETRO CARD\b",
    ],
    "Shopping": [
        r"\bAMAZON\b", r"\bFLIPKART\b", r"\bMYNTRA\b",
        r"\bAJIO\b", r"\bMEESHO\b", r"\bNYKAA\b",
        r"\bMALL\b", r"\bGARMENTS\b", r"\bFASHION\b",
        r"\bFOOTWEAR\b", r"\bSHOES\b", r"\bLAPTOP\b",
        r"\bGIFT\b", r"\bSTATIONERY\b",
    ],
    "Health & Medical": [
        r"\bPHARMACY\b", r"\bMEDICAL\b", r"\bMEDICALS\b",
        r"\bMEDICINE\b", r"\bHOSPITAL\b", r"\bCLINIC\b",
        r"\bDOCTOR\b", r"\bAPOLLO\b", r"\bMEDPLUS\b",
        r"\bNETMEDS\b", r"\bPHARMEASY\b", r"\b1MG\b",
        r"\bCHEMIST\b", r"\bDIAGNOSTIC\b",
        r"\bPATHOLOGY\b", r"\bDENTAL\b",
        r"\bHEALTHCARE\b", r"\bPATHLABS\b",
        r"\bDR LAL\b", r"\bMAX HEALTHCARE\b",
        r"\bLABORATORY\b",
    ],
    "Education": [
        r"\bBYJU\b", r"\bUNACADEMY\b", r"\bVEDANTU\b",
        r"\bSCHOOL\b", r"\bCOLLEGE\b", r"\bFEES\b",
        r"\bTUITION\b", r"\bCOACHING\b", r"\bCLASSES\b",
        r"\bACADEMY\b", r"\bINSTITUTE\b", r"\bCOURSE\b",
        r"\bLIBRARY\b", r"\bEXAM\b",
    ],
    "EMI & Loans": [
        r"\bEMI\b", r"\bLOAN\b", r"\bFINANCE\b",
        r"\bLENDING\b", r"\bCREDIT\b", r"\bBAJAJ\b",
        r"\bREPAYMENT\b", r"\bINSTALMENT\b",
    ],
    "Bills & Utilities": [
        r"\bELECTRICITY\b", r"\bBIJLI\b", r"\bPOWER\b",
        r"\bWATER\b", r"\bLPG\b", r"\bINDANE\b",
        r"\bWIFI\b", r"\bBROADBAND\b", r"\bFIBER\b",
        r"\bAIRTEL\b", r"\bBSNL\b", r"\bJIO\b",
        r"\bVODAFONE\b", r"\bDTH\b",
        r"\bRECHARGE\b",   # Fixed — now word boundary
        r"\bPOSTPAID\b", r"\bMAINTENANCE\b",
        r"\bRENT\b", r"\bSOCIETY\b",
        r"\bGAS AGENCY\b", r"\bPIPED GAS\b",
    ],
    "Investments": [
        r"\bMUTUAL FUND\b", r"\bSIP\b", r"\bZERODHA\b",
        r"\bGROWW\b", r"\bUPSTOX\b", r"\bANGEL\b",
        r"\bSHARES\b", r"\bSTOCK\b", r"\bGOLD\b",
        r"\bINSURANCE\b", r"\bPPF\b", r"\bNPS\b",
    ],
    "Gaming & Entertainment": [
        r"\bNETFLIX\b", r"\bHOTSTAR\b", r"\bSPOTIFY\b",
        r"\bYOUTUBE\b", r"\bBOOKMYSHOW\b", r"\bPVR\b",
        r"\bINOX\b", r"\bCINEMA\b", r"\bMOVIE\b",
        r"\bPLAYSTATION\b", r"\bXBOX\b", r"\bSTEAM\b",
        r"\bEPIC GAMES\b", r"\bGAMING\b",
        r"\bGOOGLE PLAY\b",
    ],
    "Travel & Hotels": [
        r"\bOYO\b", r"\bAIRBNB\b", r"\bFLIGHT\b",
        r"\bINDIGO\b", r"\bAIRINDIA\b", r"\bSPICEJET\b",
        r"\bHOLIDAY\b", r"\bTOUR\b",
        r"\bGOIBIBO\b", r"\bMAKEMYTRIP\b",
        r"\bHOTEL ADVANCE\b", r"\bTREEBO\b",
    ],
    "Personal Care": [
        r"\bSALON\b", r"\bSALOON\b", r"\bBARBER\b",
        r"\bPARLOUR\b", r"\bSPA\b", r"\bMASSAGE\b",
        r"\bGROOMING\b", r"\bMEHENDI\b", r"\bNAILS\b",
    ],
}

UNNECESSARY = [
    "Food & Dining", "Shopping",
    "Gaming & Entertainment", "Travel & Hotels",
    "Personal Care",
]
NECESSARY = [
    "Health & Medical", "Education",
    "EMI & Loans", "Bills & Utilities", "Investments",
]

COMPILED_INDIAN_KEYWORDS = {
    category: [(pattern, pattern.replace(r"\b", "").strip(), re.compile(pattern)) for pattern in patterns]
    for category, patterns in INDIAN_KEYWORDS.items()
}

CLEAN_AMOUNT_PATTERN = re.compile(r"[₹,\s]")
MONTH_PATTERN_1 = re.compile(
    r"\b(\d{1,2})\s+"
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"\s+(\d{4})\b",
    re.IGNORECASE
)
MONTH_PATTERN_2 = re.compile(r"\b(\d{2})[/-](\d{2})[/-](\d{4})\b")
MONTH_PATTERN_3 = re.compile(r"\b(\d{4})[/-](\d{2})[/-](\d{2})\b")

COMPILED_WORD_PATTERNS = {
    w: re.compile(r"\b" + re.escape(w) + r"\b")
    for keyword in SUBS_DB
    for w in keyword.upper().split()
}

# ════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════

def clean_amount(val):
    if not val:
        return None
    cleaned = CLEAN_AMOUNT_PATTERN.sub("", str(val)).strip()
    try:
        f = float(cleaned)
        return f if f > 0 else None
    except:
        return None

def is_annual_desc(description):
    return any(kw in description.upper()
               for kw in ANNUAL_KEYWORDS)

def extract_month(text):
    if not text:
        return None
    m = MONTH_PATTERN_1.search(text)
    if m:
        return m.group(2).capitalize()
    m = MONTH_PATTERN_2.search(text)
    if m:
        return MONTH_MAP.get(m.group(2))
    m = MONTH_PATTERN_3.search(text)
    if m:
        return MONTH_MAP.get(m.group(2))
    return None

def smart_categorise(description):
    """Word boundary matching — no false positives."""
    desc_upper = description.upper()
    scores     = defaultdict(int)
    for category, patterns_data in COMPILED_INDIAN_KEYWORDS.items():
        for orig_pattern, word, compiled_pattern in patterns_data:
            if compiled_pattern.search(desc_upper):
                scores[category] += len(word.split())
    if not scores:
        return "Other", 0
    best = max(scores, key=scores.get)
    return best, min(scores[best] * 25, 100)

def is_header_row(cells):
    joined = " ".join(
        str(c).upper().strip() if c else ""
        for c in cells
    )
    signals = [
        "DESCRIPTION", "NARRATION", "DEBIT",
        "CREDIT", "BALANCE", "TXN DATE",
        "PARTICULARS", "WITHDRAWAL",
    ]
    return (any(h in joined for h in signals)
            and len(joined) < 300)

# ════════════════════════════════════════════════════════════
#  FIX 2 — DYNAMIC COLUMN DETECTION
#  Reads header to find correct debit column
#  Won't confuse CREDIT or BALANCE with DEBIT
# ════════════════════════════════════════════════════════════

DEBIT_HEADERS = [
    "DEBIT", "DR", "WITHDRAWAL", "WITHDRAWL",
    "AMOUNT(DR)", "DEBIT(INR)", "DR AMOUNT",
    "WITHDRAWALS", "DEBIT AMOUNT",
]
DESC_HEADERS = [
    "DESCRIPTION", "NARRATION", "PARTICULARS",
    "DETAILS", "TRANSACTION DETAILS", "REMARKS",
]

def detect_columns(header_row):
    desc_idx  = None
    debit_idx = None
    cells_up  = [
        str(c).upper().strip() if c else ""
        for c in header_row
    ]
    for i, cell in enumerate(cells_up):
        if any(kw in cell for kw in DESC_HEADERS):
            if desc_idx is None:
                desc_idx = i
        # Strict match — DEBIT only, not CREDIT/BALANCE
        if any(kw == cell or kw in cell
               for kw in DEBIT_HEADERS):
            if debit_idx is None:
                debit_idx = i
    return desc_idx, debit_idx
def process_pdf(file, password=None):

    # ════════════════════════════════════════════════════════════
    #  PDF READER ENGINE
    # ════════════════════════════════════════════════════════════

    transactions  = []
    full_text     = ""
    current_month = None

    try:
        # Auto-detect if password needed
        try:
            with pdfplumber.open(
                io.BytesIO(file) if isinstance(file, bytes)
                else file
            ) as t:
                t.pages[0].extract_text()
            password_needed = False
        except Exception:
            password_needed = True

        open_kwargs = {}
        if password_needed and password:
            open_kwargs["password"] = password

        file_obj = (
            io.BytesIO(file)
            if isinstance(file, bytes) else file
        )

        with pdfplumber.open(
            file_obj, **open_kwargs
        ) as pdf:
            pages     = len(pdf.pages)
            desc_idx  = None
            debit_idx = None

            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    full_text += t + "\n"

                for table in (page.extract_tables() or []):
                    # Find header row first
                    for row in table:
                        if row and is_header_row(row):
                            desc_idx, debit_idx = \
                                detect_columns(row)
                            break

                    for row in table:
                        if not row or len(row) < 3:
                            continue

                        cells = [
                            str(c).strip() if c else ""
                            for c in row
                        ]

                        if is_header_row(row):
                            continue

                        # Extract month from date column
                        month_from_row = extract_month(
                            cells[0]
                        )
                        if month_from_row:
                            current_month = month_from_row

                        description = ""
                        debit       = None

                        # Use dynamic columns if detected
                        if (desc_idx is not None
                                and debit_idx is not None
                                and desc_idx < len(cells)
                                and debit_idx < len(cells)):
                            description = cells[desc_idx]
                            debit = clean_amount(
                                cells[debit_idx]
                            )
                        else:
                            # Fallback positional
                            if len(cells) >= 6:
                                description = cells[1]
                                debit = clean_amount(
                                    cells[3]
                                )
                            elif len(cells) >= 4:
                                description = cells[1]
                                debit = clean_amount(
                                    cells[2]
                                )

                        if not description or not debit:
                            continue

                        # Skip credits and income
                        desc_upper = description.upper()
                        if any(skip in desc_upper
                               for skip in [
                                   "TRF FROM", "SALARY",
                                   "INTEREST CREDIT",
                                   "NEFT CR", "IMPS CR",
                                   "REFUND", "CASHBACK",
                                   "REVERSAL",
                               ]):
                            continue

                        if 1 <= debit <= 200000:
                            transactions.append({
                                "description": description,
                                "debit":       debit,
                                "is_annual":   is_annual_desc(
                                    description
                                ),
                                "month": current_month
                                         or "Unknown",
                            })

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

    if not transactions and not full_text.strip():
        return None

    # ════════════════════════════════════════════════════════════
    #  SUBSCRIPTION DETECTION
    #  Uses word boundaries for accurate matching
    # ════════════════════════════════════════════════════════════

    found_subs = []
    seen       = set()

    for keyword, info in SUBS_DB.items():
        pattern_regex = COMPILED_SUBS_PATTERNS[keyword]
        matched_txn = None

        for txn in transactions:
            if pattern_regex.search(txn["description"].upper()):
                matched_txn = txn
                break

        # Also check raw text as fallback
        if not matched_txn and not pattern_regex.search(full_text.upper()):
            continue

        key = keyword.split()[0]
        if key in seen:
            continue
        seen.add(key)

        actual_price = (
            matched_txn["debit"]
            if matched_txn
            else info["price"]
        )

        # Cap unreasonably large amounts
        if actual_price > 50000:
            actual_price = info["price"]

        display_name = keyword.title()
        frequency = "monthly"

        # Detect billing cycle from amount ratio
        if info["price"] > 1:
            try:
                ratio = actual_price / info["price"]
                if ratio >= 9:
                    display_name += " (Annual)"
                    frequency = "annual"
                elif ratio >= 5:
                    display_name += " (6-Month)"
                    frequency = "6-month"
                elif ratio >= 2.5:
                    display_name += " (Quarterly)"
                    frequency = "quarterly"
            except ZeroDivisionError:
                pass

        # Count occurrences for forgotten detection
        name_words = [
            w for w in keyword.upper().split()
            if len(w) > 3
        ]
        count = sum(
            1 for txn in transactions
            if any(
                COMPILED_WORD_PATTERNS.get(w) and COMPILED_WORD_PATTERNS.get(w).search(txn["description"].upper())
                for w in name_words
            )
        )

        found_subs.append({
            "name":             display_name,
            "amount":           actual_price,
            "frequency":        frequency,
            "count":            count,
            "keyword":          keyword,
            "cancellation_url": CANCELLATION_URLS.get(keyword, "")
        })

    # ════════════════════════════════════════════════════════════
    #  CATEGORISATION
    # ════════════════════════════════════════════════════════════

    categorised   = defaultdict(list)
    uncategorised = []

    for txn in transactions:
        cat, conf = smart_categorise(txn["description"])
        txn["category"] = cat
        if cat == "Other":
            uncategorised.append(txn)
        else:
            categorised[cat].append(txn)

    # ════════════════════════════════════════════════════════════
    #  MONTHLY BREAKDOWN
    # ════════════════════════════════════════════════════════════

    seen_months     = []
    monthly_summary = defaultdict(lambda: defaultdict(float))

    for txn in transactions:
        m = txn.get("month", "Unknown")
        if not m or m == "Unknown":
            continue
        if m not in seen_months:
            seen_months.append(m)
        cat = txn.get("category", "Other")
        if cat != "Other":
            monthly_summary[m][cat] += txn["debit"]

    monthly_totals = {
        m: sum(monthly_summary[m].values())
        for m in seen_months
    }

    # ════════════════════════════════════════════════════════════
    #  TOTALS & HEALTH SCORE
    # ════════════════════════════════════════════════════════════

    grand_total = sum(
        t["debit"] for txns in categorised.values()
        for t in txns
    )
    necessary_total = sum(
        sum(t["debit"] for t in categorised.get(cat, []))
        for cat in NECESSARY
    )
    unnecessary_total = sum(
        sum(t["debit"] for t in categorised.get(cat, []))
        for cat in UNNECESSARY
    )

    # Forgotten subs — charged only once in statement period
    forgotten_subs = [
        s for s in found_subs
        if s["count"] == 1
        and "(Annual)" not in s["name"]
        and "(6-Month)" not in s["name"]
        and "(Quarterly)" not in s["name"]
    ]

    # Health score — behaviour based not just total
    sub_monthly = sum(
        s["amount"] for s in found_subs
        if "(Annual)" not in s["name"]
    )
    sub_score = (
        25 if sub_monthly == 0 else
        22 if sub_monthly <= 500 else
        18 if sub_monthly <= 1000 else
        12 if sub_monthly <= 2000 else
        7  if sub_monthly <= 3000 else 3
    )
    nec_pct = (
        (necessary_total / grand_total * 100)
        if grand_total > 0 else 50
    )
    bal_score = (
        25 if nec_pct >= 60 else
        20 if nec_pct >= 45 else
        14 if nec_pct >= 30 else
        8  if nec_pct >= 15 else 3
    )
    forg_score = (
        25 if len(forgotten_subs) == 0 else
        18 if len(forgotten_subs) == 1 else
        11 if len(forgotten_subs) == 2 else 5
    )
    health_score = min(
        sub_score + bal_score + forg_score + 15, 100
    )

    # Category spending totals for charts
    category_totals = {}
    for cat, txns in categorised.items():
        total = sum(t["debit"] for t in txns)
        if total > 0:
            category_totals[cat] = total

    # ════════════════════════════════════════════════════════════
    #  RETURN — Complete data for frontend
    # ════════════════════════════════════════════════════════════

    return {
        # Summary metrics
        "total_spent":        grand_total,
        "transaction_count":  len(transactions),
        "subscriptions_found": found_subs,
        "health_score":       health_score,

        # Spending breakdown for charts
        "category_totals":    category_totals,
        "necessary_total":    necessary_total,
        "unnecessary_total":  unnecessary_total,

        # Forgotten subscriptions
        "forgotten_subs":     forgotten_subs,
        "forgotten_cost":     sum(
            s["amount"] * 12 for s in forgotten_subs
        ),

        # Monthly data for trends
        "monthly_totals":     monthly_totals,
        "seen_months":        seen_months,

        # Raw transactions for Excel export
        "transactions":       transactions,
    }
