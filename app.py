## LEGASAFE — Complete All-in-One v14
## Cell 1: !pip install pdfplumber
## Cell 2: This entire file — everything in one cell
## NEW: Financial Health Score — single number summary
## TWO input methods: PDF upload OR SMS paste

import io
import re
from collections import defaultdict
from datetime import datetime

import pdfplumber

import csv
import pandas as pd

def run_legasafe():
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

  CANCEL_GUIDE = {
      "Netflix":             ["1. Open Netflix app",
                              "2. Tap Profile → Account",
                              "3. Tap Cancel Membership",
                              "4. Confirm cancellation"],
      "Spotify":             ["1. Go to account.spotify.com",
                              "2. Click Your Plan",
                              "3. Click Cancel Premium",
                              "4. Confirm cancellation"],
      "Hotstar":             ["1. Open Hotstar app",
                              "2. Tap Profile → Manage Subscription",
                              "3. Tap Cancel Subscription",
                              "4. Confirm cancellation"],
      "Amazon":              ["1. Go to amazon.in",
                              "2. Account → Prime Membership",
                              "3. Click Manage → End Membership",
                              "4. Confirm cancellation"],
      "Amazon Prime":        ["1. Go to amazon.in",
                              "2. Account → Prime Membership",
                              "3. Click Manage → End Membership",
                              "4. Confirm cancellation"],
      "Zomato":              ["1. Open Zomato app",
                              "2. Tap Profile → Zomato Gold/Pro",
                              "3. Tap Cancel Plan",
                              "4. Confirm cancellation"],
      "Swiggy":              ["1. Open Swiggy app",
                              "2. Tap Profile → Swiggy One",
                              "3. Tap Cancel Membership",
                              "4. Confirm cancellation"],
      "Youtube":             ["1. Go to myaccount.google.com",
                              "2. Payments & Subscriptions",
                              "3. Click YouTube Premium → Cancel",
                              "4. Confirm cancellation"],
      "Youtube Premium":     ["1. Go to myaccount.google.com",
                              "2. Payments & Subscriptions",
                              "3. Click YouTube Premium → Cancel",
                              "4. Confirm cancellation"],
      "Google One":          ["1. Go to one.google.com",
                              "2. Click Settings → Cancel Plan",
                              "3. Confirm cancellation"],
      "Icloud":              ["1. iPhone Settings → Apple ID",
                              "2. Tap Subscriptions → iCloud+",
                              "3. Tap Cancel Subscription",
                              "4. Confirm cancellation"],
      "Canva":               ["1. Go to canva.com",
                              "2. Account Settings → Billing",
                              "3. Click Cancel Plan",
                              "4. Confirm cancellation"],
      "Linkedin":            ["1. Go to linkedin.com",
                              "2. Me → Settings → Subscriptions",
                              "3. Click Cancel Subscription",
                              "4. Confirm cancellation"],
      "Microsoft":           ["1. Go to account.microsoft.com",
                              "2. Services & Subscriptions",
                              "3. Find Microsoft 365 → Cancel",
                              "4. Confirm cancellation"],
      "Playstation":         ["1. Go to store.playstation.com",
                              "2. Account → Subscriptions",
                              "3. Click Cancel Subscription",
                              "4. Confirm cancellation"],
      "Playstation Network": ["1. Go to store.playstation.com",
                              "2. Account → Subscriptions",
                              "3. Click Cancel Subscription",
                              "4. Confirm cancellation"],
      "Steam":               ["1. Open Steam app",
                              "2. Account → Manage Subscriptions",
                              "3. Click Cancel Subscription",
                              "4. Confirm cancellation"],
      "Epic Games":          ["1. Go to epicgames.com",
                              "2. Account → Subscriptions",
                              "3. Click Cancel Subscription",
                              "4. Confirm cancellation"],
      "Unacademy":           ["1. Open Unacademy app",
                              "2. Profile → Subscription",
                              "3. Tap Cancel Plan",
                              "4. Confirm cancellation"],
      "Byju":                ["1. Call 1800-102-9579 (toll free)",
                              "2. Say 'Cancel Subscription'",
                              "3. Give registered number",
                              "4. Get SMS confirmation"],
      "Tinder":              ["1. Open Tinder app",
                              "2. Profile → Manage Subscription",
                              "3. Tap Cancel Subscription",
                              "4. Confirm cancellation"],
      "Audible":             ["1. Go to audible.in",
                              "2. Account Details",
                              "3. Cancel Membership",
                              "4. Confirm cancellation"],
      "Adobe":               ["1. Go to account.adobe.com",
                              "2. Click Plans & Payment",
                              "3. Click Cancel Plan",
                              "4. Confirm cancellation"],
      "Notion":              ["1. Go to notion.so",
                              "2. Settings → Billing",
                              "3. Click Cancel Plan",
                              "4. Confirm cancellation"],
      "Grammarly":           ["1. Go to grammarly.com",
                              "2. Account → Subscription",
                              "3. Click Cancel Plan",
                              "4. Confirm cancellation"],
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
      return any(kw in description.upper()
                for kw in ANNUAL_KEYWORDS)

  def extract_month(text):
      if not text:
          return None
      m = re.search(
          r"\b(\d{1,2})\s+"
          r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
          r"\s+(\d{4})\b",
          text, re.IGNORECASE
      )
      if m:
          return m.group(2).capitalize()
      m = re.search(r"\b(\d{2})[/-](\d{2})[/-](\d{4})\b", text)
      if m:
          return MONTH_MAP.get(m.group(2))
      m = re.search(r"\b(\d{4})[/-](\d{2})[/-](\d{2})\b", text)
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

  def get_waste_score(monthly_total, count):
      score = 0
      if monthly_total > 3000:    score += 4
      elif monthly_total > 2000:  score += 3
      elif monthly_total > 1000:  score += 2
      else:                       score += 1
      if count > 8:               score += 3
      elif count > 5:             score += 2
      elif count > 3:             score += 1
      return min(score, 10)

  def score_label(s):
      if s <= 3: return "🟢 Healthy"
      if s <= 6: return "🟡 Moderate"
      if s <= 8: return "🟠 Concerning"
      return            "🔴 Critical"

  # ════════════════════════════════════════════════════════════
  #  FINANCIAL HEALTH SCORE ENGINE
  # ════════════════════════════════════════════════════════════

  def calculate_health_score(
      found_subs, grand_total, necessary_total,
      unnecessary_total, over_budget, forgotten_subs,
      monthly_totals, categorised
  ):
      """
      Calculate a Financial Health Score out of 100.

      Four pillars:
      1. Subscription Control  (25 pts) — fewer/managed = better
      2. Spending Balance      (25 pts) — necessary > unnecessary
      3. Budget Discipline     (25 pts) — under budget = better
      4. Financial Awareness   (25 pts) — no forgotten subs = better
      """

      scores = {}

      # ── 1. Subscription Control (25 pts) ─────────────────
      sub_count    = len(found_subs)
      monthly_subs = sum(s["monthly_equiv"] for s in found_subs
                        if not s["is_annual"])

      if sub_count == 0:
          sub_score = 25
      elif sub_count <= 3 and monthly_subs <= 500:
          sub_score = 22
      elif sub_count <= 5 and monthly_subs <= 1000:
          sub_score = 18
      elif sub_count <= 8 and monthly_subs <= 2000:
          sub_score = 12
      elif sub_count <= 12 and monthly_subs <= 3000:
          sub_score = 7
      else:
          sub_score = 3

      scores["💸 Subscription Control"] = sub_score

      # ── 2. Spending Balance (25 pts) ──────────────────────
      if grand_total > 0:
          necessary_pct = (necessary_total / grand_total) * 100
          if necessary_pct >= 60:
              bal_score = 25
          elif necessary_pct >= 45:
              bal_score = 20
          elif necessary_pct >= 30:
              bal_score = 14
          elif necessary_pct >= 15:
              bal_score = 8
          else:
              bal_score = 3
      else:
          bal_score = 15  # neutral if no data

      scores["📊 Spending Balance"] = bal_score

      # ── 3. Budget Discipline (25 pts) ─────────────────────
      total_cats  = max(len(over_budget) +
                        (25 - len(over_budget)), 1)
      over_count  = len(over_budget)

      if over_count == 0:
          bud_score = 25
      elif over_count == 1:
          bud_score = 20
      elif over_count == 2:
          bud_score = 14
      elif over_count == 3:
          bud_score = 9
      else:
          bud_score = 4

      scores["🎯 Budget Discipline"] = bud_score

      # ── 4. Financial Awareness (25 pts) ───────────────────
      forgotten_count = len(forgotten_subs)

      if forgotten_count == 0:
          aware_score = 25
      elif forgotten_count == 1:
          aware_score = 18
      elif forgotten_count == 2:
          aware_score = 11
      else:
          aware_score = 5

      scores["🔍 Financial Awareness"] = aware_score

      # ── Total ──────────────────────────────────────────────
      total = sum(scores.values())

      return total, scores

  def health_label(score):
      if score >= 85: return "🟢 Excellent"
      if score >= 70: return "🟢 Good"
      if score >= 55: return "🟡 Moderate"
      if score >= 40: return "🟠 Needs Work"
      return                 "🔴 Poor"

  def health_bar(score):
      filled = int(score / 5)
      empty  = 20 - filled
      return "█" * filled + "░" * empty

  def get_top_actions(found_subs, over_budget_cats,
                      forgotten_subs, unnecessary_total,
                      categorised):
      """Generate top 3 personalised action items."""
      actions = []

      # Action 1: Cancel biggest forgotten sub
      if forgotten_subs:
          biggest = max(forgotten_subs,
                        key=lambda x: x["yearly_cost"])
          actions.append(
              f"Cancel {biggest['name']} → "
              f"save ₹{biggest['yearly_cost']:,.0f}/yr"
          )

      # Action 2: Biggest over-budget category
      if over_budget_cats:
          actions.append(
              f"Reduce {over_budget_cats[0].split()[0]} "
              f"spending — it's over your budget"
          )

      # Action 3: Investment nudge
      investment_spend = sum(
          t["debit"] for t in
          categorised.get("💰 Investments", [])
      )
      if investment_spend == 0:
          actions.append(
              "Start a SIP of ₹500/month → "
              "₹6,000/year working for you"
          )
      elif unnecessary_total > 3000:
          savings = int(unnecessary_total * 0.2)
          actions.append(
              f"Invest ₹{savings:,}/mo from "
              f"non-essential savings"
          )

      # Fill remaining with generic advice
      generic = [
          "Review all subscriptions quarterly",
          "Set budget alerts for top 3 categories",
          "Track spending weekly not monthly",
      ]
      for g in generic:
          if len(actions) >= 3:
              break
          actions.append(g)

      return actions[:3]

  # ════════════════════════════════════════════════════════════
  #  SMS HELPER FUNCTIONS
  # ════════════════════════════════════════════════════════════

  def extract_sms_amount(sms_text):
      patterns = [
          r"(?:Rs\.?|INR|₹)\s*"
          r"(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)",
          r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/-)",
      ]
      for pat in patterns:
          m = re.search(pat, sms_text, re.IGNORECASE)
          if m:
              try:
                  val = float(m.group(1).replace(",", ""))
                  if 1 <= val <= 100000:
                      return val
              except:
                  continue
      return None

  def extract_sms_merchant(sms_text):
      upper = sms_text.upper()
      m     = re.search(
          r"(?:TO|AT|FOR|TOWARDS)\s+"
          r"([A-Z][A-Z0-9\s]{2,30}?)"
          r"(?:\.|,|\s+ON|\s+AVL|\s+REF|\n|$)",
          upper
      )
      if m:
          merchant = m.group(1).strip()
          if len(merchant) > 2:
              return merchant
      return None

  def is_debit_sms(sms_text):
      return any(kw in sms_text.upper() for kw in [
          "DEBITED", "DEBIT", "PAID", "SPENT",
          "TRANSFERRED", "WITHDRAWN", "PURCHASE",
      ])

  def match_subscription_sms(text):
      text_upper = text.upper()
      for keyword, info in SUBS_DB.items():
          if keyword in text_upper:
              return keyword, info
      return None, None

  # ════════════════════════════════════════════════════════════
  #  STEP 1 — CHOOSE INPUT METHOD
  # ════════════════════════════════════════════════════════════

  print("━" * 60)
  print("  🛡️  LEGASAFE v12 — Complete Financial Analyser")
  print("  Subscriptions · Spending · Health Score · Trends")
  print("  100% local. Your data never leaves this device.")
  print("━" * 60)
  print()
  print("  How do you want to analyse your spending?")
  print()
  print("  1️⃣  Upload bank statement PDF")
  print("  2️⃣  Paste bank SMS alerts (no PDF needed)")
  print()

  input_choice = input("  Enter 1 or 2: ").strip()

  # ════════════════════════════════════════════════════════════
  #  INPUT METHOD 2 — SMS PARSER
  # ════════════════════════════════════════════════════════════

  if input_choice == "2":
      print()
      print("━" * 60)
      print("  📱 SMS BANK ALERT PARSER")
      print("━" * 60)
      print()
      print("  Paste bank SMS alerts. Empty line = new SMS.")
      print("  Type DONE when finished.\n")

      sms_lines  = []
      sms_buffer = []

      while True:
          line = input()
          if line.strip().upper() == "DONE":
              if sms_buffer:
                  sms_lines.append(" ".join(sms_buffer))
              break
          elif line.strip() == "":
              if sms_buffer:
                  sms_lines.append(" ".join(sms_buffer))
                  sms_buffer = []
          else:
              sms_buffer.append(line.strip())

      parsed_txns   = []
      subscriptions = []
      other_debits  = []

      for sms in sms_lines:
          if not sms.strip() or not is_debit_sms(sms):
              continue
          amount   = extract_sms_amount(sms)
          merchant = extract_sms_merchant(sms)
          if not amount:
              continue
          sub_key, sub_info = match_subscription_sms(
              merchant or sms
          )
          txn = {
              "sms":      sms,
              "amount":   amount,
              "merchant": merchant or "Unknown",
              "sub_key":  sub_key,
              "sub_info": sub_info,
          }
          if sub_key:
              subscriptions.append(txn)
          else:
              other_debits.append(txn)
          parsed_txns.append(txn)

      now = datetime.now().strftime("%d %b %Y, %I:%M %p")
      print()
      print("━" * 60)
      print(f"  🛡️  LEGASAFE SMS REPORT  —  {now}")
      print("━" * 60)

      seen  = set()
      unique_subs = []
      for t in subscriptions:
          if t["sub_key"] not in seen:
              seen.add(t["sub_key"])
              unique_subs.append(t)

      total = sum(t["amount"] for t in subscriptions)

      if unique_subs:
          print(f"\n  📋 SUBSCRIPTIONS: {len(unique_subs)} found")
          print(f"  {'─'*54}")
          for i, t in enumerate(unique_subs, 1):
              print(f"  {i:>2}. {t['sub_key'].title():<28} "
                    f"₹{t['amount']:>7,.0f}/mo")
          print(f"\n  💸 Monthly: ₹{total:,.0f}")
          print(f"  📅 Yearly:  ₹{total*12:,.0f}")

          # SMS Health Score (simplified)
          sub_score = max(0, 25 - (len(unique_subs) * 3))
          sms_health = sub_score + 15 + 20 + 20  # partial score
          print(f"\n  {'─'*54}")
          print(f"  🏆 PARTIAL HEALTH SCORE: {sms_health}/100")
          print(f"  {health_bar(sms_health)}")
          print(f"  {health_label(sms_health)}")
          print(f"  (Upload PDF for full score)")

          print(f"\n  {'─'*54}")
          print(f"  ❌ CANCELLATION GUIDES")
          for t in unique_subs:
              guide = CANCEL_GUIDE.get(t["sub_key"].title())
              if guide:
                  print(f"\n  {t['sub_key'].title()}")
                  for step in guide:
                      print(f"     {step}")

      if not parsed_txns:
          print(f"\n  ⚠️ No debit transactions found.")

      if unique_subs:
          print(f"""
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    💬 SHARE ON WHATSAPP

    🛡️ *Legasafe SMS Report*
    • {len(unique_subs)} subscriptions | ₹{total*12:,.0f}/yr
    • Health Score: {sms_health}/100 {health_label(sms_health)}
    Try free 👉 aksharrajput4-netizen.github.io/Legasafe
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          """)

  # ════════════════════════════════════════════════════════════
  #  INPUT METHOD 1 — PDF UPLOAD
  # ════════════════════════════════════════════════════════════

  else:
      print()
      print("📄 Upload your bank statement PDF...")
      uploaded  = files.upload()

      # --- THE CANCEL SAFETY NET ---
      if not uploaded:
          print("\n  ⚠️ Upload cancelled. Run the cell again to restart.")
          return
      # -----------------------------

      filename  = list(uploaded.keys())[0]
      pdf_bytes = uploaded[filename]

      password = input(
          "\n🔐 PDF password? (Press Enter to skip): "
      ).strip()

      transactions  = []
      full_text     = ""
      current_month = None

      try:
          try:
              with pdfplumber.open(
                      io.BytesIO(pdf_bytes)) as t:
                  t.pages[0].extract_text()
              password_needed = False
          except Exception:
              password_needed = True

          if password and not password_needed:
              print("  ⚠️ PDF not password protected.")
          if password_needed and not password:
              print("  🔐 PDF requires a password.")
              password = input("  Enter password: ").strip()

          with pdfplumber.open(
            io.BytesIO(pdf_bytes),
            password=password if password_needed and password else None
        ) as pdf:
            pages = len(pdf.pages)

            # --- THE FIX: Track columns dynamically ---
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

                        # --- 1. Find the Headers dynamically ---
                        if any(h in joined for h in ["DATE", "DESCRIPTION", "NARRATION", "DEBIT", "WITHDRAWAL", "PARTICULARS"]) and len(joined) < 200:
                            for i, cell in enumerate(cells):
                                cell_up = cell.upper()
                                if any(x in cell_up for x in ["DESC", "NARRATION", "PARTICULARS"]):
                                    desc_idx = i
                                if any(x in cell_up for x in ["DEBIT", "WITHDRAWAL", "AMOUNT"]):
                                    debit_idx = i
                            continue # Skip the header row itself

                        # --- 2. Extract Data using our new column map ---
                        month_from_row = extract_month(cells[0])
                        if month_from_row:
                            current_month = month_from_row

                        description = ""
                        debit       = None

                        # If we successfully found the headers, pull from exact columns!
                        if desc_idx != -1 and debit_idx != -1 and len(cells) > max(desc_idx, debit_idx):
                            description = cells[desc_idx]
                            debit       = clean_amount(cells[debit_idx])
                        # Fallback for weirdly formatted pages that don't have clear headers
                        elif len(cells) >= 6:
                            description = cells[1]
                            debit       = clean_amount(cells[3])
                        elif len(cells) == 5:
                            description = cells[1]
                            debit       = clean_amount(cells[2])
                        elif len(cells) == 4:
                            description = cells[1]
                            debit       = clean_amount(cells[2])

                        if not description or not debit:
                            continue

                        desc_upper = description.upper()
                        # Filter out internal bank transfers and incoming money
                        if any(skip in desc_upper for skip in ["TRF FROM", "SALARY", "INTEREST CREDIT", "NEFT CR", "IMPS CR", "REFUND", "CASHBACK", "REVERSAL"]):
                            continue

                        if 1 <= debit <= 200000:
                            transactions.append({
                                "description": description,
                                "debit":       debit,
                                "is_annual":   is_annual_desc(description),
                                "month":       current_month or "Unknown",
                            })
          print(f"   ✅ Read {pages} page(s) — "
                f"Found {len(transactions)} transactions")

      except Exception as e:
          print(f"\n❌ Error: {e}")
          raise SystemExit

      # ── Set Budgets ───────────────────────────────────────
      print()
      print("━" * 60)
      print("  💰 MONTHLY BUDGET ALERTS")
      print("━" * 60)

      want_budgets = input(
          "\n  Set monthly budgets? (yes/no): "
      ).strip().lower()

      budgets = {}
      if want_budgets in ["yes", "y", "haan", "ha", "1"]:
          print("\n  Press Enter for default.\n")
          for cat, default in DEFAULT_BUDGETS.items():
              user_input = input(
                  f"  {cat:<32} [₹{default:,}]: "
              ).strip()
              budgets[cat] = (int(user_input)
                              if user_input.isdigit()
                              else default)
          print("\n  ✅ Budgets set.")
      else:
          budgets = DEFAULT_BUDGETS.copy()
          print("  ✅ Using default budgets.")

      print("  Analysing...")

      # ── Detect Subscriptions ──────────────────────────────
      found_subs = []
      seen       = set()
      for keyword, info in SUBS_DB.items():
          keyword_upper = keyword.upper()
          matched_txn   = None
          for txn in transactions:
              if keyword_upper in txn["description"].upper():
                  matched_txn = txn
                  break
          if not matched_txn and \
                  keyword_upper not in full_text.upper():
              continue
          key = keyword.split()[0]
          if key in seen:
              continue
          seen.add(key)
          annual = matched_txn["is_annual"] \
                  if matched_txn else False
          actual = matched_txn["debit"] \
                  if matched_txn else None
          if actual:
              if not annual and actual > 10000:
                  actual = None
              if annual and actual > 50000:
                  actual = None
          base_price = actual if actual else info["price"]
          found_subs.append({
              "name":          keyword.title(),
              "category":      info["cat"],
              "amount":        base_price,
              "confirmed":     actual is not None,
              "is_annual":     annual,
              "yearly_cost":   base_price if annual
                              else base_price * 12,
              "monthly_equiv": round(base_price / 12, 0)
                              if annual else base_price,
          })

      # ── Categorise ────────────────────────────────────────
      categorised   = defaultdict(list)
      uncategorised = []
      for txn in transactions:
          cat, conf = smart_categorise(txn["description"])
          entry     = {**txn, "confidence": conf}
          if "Unknown" in cat:
              uncategorised.append(entry)
          else:
              categorised[cat].append(entry)

      # ── Monthly ───────────────────────────────────────────
      seen_months     = []
      monthly_summary = defaultdict(lambda: defaultdict(float))
      for txn in transactions:
          m = txn.get("month", "Unknown")
          if not m or m == "Unknown":
              continue
          if m not in seen_months:
              seen_months.append(m)
          cat, _ = smart_categorise(txn["description"])
          if "Unknown" not in cat:
              monthly_summary[m][cat] += txn["debit"]
      monthly_totals = {
          m: sum(monthly_summary[m].values())
          for m in seen_months
      }

      # ── Spending totals ───────────────────────────────────
      grand_total = sum(
          t["debit"] for txns in categorised.values()
          for t in txns
      )
      necessary_total   = sum(
          sum(t["debit"] for t in categorised.get(cat, []))
          for cat in NECESSARY
      )
      unnecessary_total = sum(
          sum(t["debit"] for t in categorised.get(cat, []))
          for cat in UNNECESSARY
      )

      # ── Budget alerts ─────────────────────────────────────
      months_count  = max(len(seen_months), 1)
      over_budget   = []
      near_budget   = []
      under_budget  = []
      for cat, budget in budgets.items():
          total_spent = sum(
              t["debit"] for t in categorised.get(cat, [])
          )
          avg_monthly = total_spent / months_count
          if avg_monthly == 0:
              continue
          pct = (avg_monthly / budget * 100) \
                if budget > 0 else 0
          if pct > 100:
              over_budget.append(cat)
          elif pct > 80:
              near_budget.append(cat)
          else:
              under_budget.append(cat)

      # ── Forgotten subs ────────────────────────────────────
      forgotten_subs = []
      for sub in found_subs:
          if sub["is_annual"]:
              continue
          count      = 0
          name_words = [w for w in sub["name"].upper().split()
                        if len(w) > 3]
          for txn in transactions:
              if any(w in txn["description"].upper()
                    for w in name_words):
                  count += 1
          if count == 1:
              forgotten_subs.append(sub)

      # ════════════════════════════════════════════════════
      #  PRINT FULL REPORT
      # ════════════════════════════════════════════════════

      now = datetime.now().strftime("%d %b %Y, %I:%M %p")
      print()
      print("━" * 60)
      print(f"  🛡️  LEGASAFE REPORT  —  {now}")
      print("━" * 60)

      # ── FINANCIAL HEALTH SCORE ────────────────────────
      total_score, pillar_scores = calculate_health_score(
          found_subs, grand_total, necessary_total,
          unnecessary_total, over_budget, forgotten_subs,
          monthly_totals, categorised
      )
      top_actions = get_top_actions(
          found_subs, over_budget, forgotten_subs,
          unnecessary_total, categorised
      )

      print()
      print("━" * 60)
      print("  🏆 YOUR FINANCIAL HEALTH SCORE")
      print("━" * 60)
      print()
      print(f"  {health_bar(total_score)}  "
            f"{total_score}/100")
      print()
      print(f"  Overall: {health_label(total_score)}")
      # --- NEW FEATURE 1: EMERGENCY FUND CHECK ---
      emergency_target = grand_total * 3
      print(f"\n  {'-'*54}")
      print(f"  🛡️ EMERGENCY FUND CHECK")
      print(f"  {'-'*54}")
      print(f"  To be financially safe, you should aim for a cash reserve of ₹{emergency_target:,.0f}.")
      if grand_total > necessary_total:
          print("  Action: You are spending more on luxuries than essentials. Consider reallocating!")
      print()
      print(f"  {'─'*54}")
      print(f"  PILLAR BREAKDOWN")
      print(f"  {'─'*54}")
      for pillar, pts in pillar_scores.items():
          bar   = "█" * pts + "░" * (25 - pts)
          label = ("🟢" if pts >= 20 else
                  "🟡" if pts >= 13 else "🔴")
          print(f"  {pillar:<28} {bar}  {pts}/25  {label}")

      print(f"\n  {'─'*54}")
      print(f"  🎯 TOP 3 ACTIONS TO IMPROVE YOUR SCORE")
      print(f"  {'─'*54}")
      for i, action in enumerate(top_actions, 1):
          print(f"  {i}. {action}")

      # ── Subscriptions ─────────────────────────────────
      if found_subs:
          monthly_total = sum(
              s["monthly_equiv"] for s in found_subs
              if not s["is_annual"]
          )
          annual_total = sum(
              s["yearly_cost"] for s in found_subs
              if s["is_annual"]
          )
          true_yearly  = (monthly_total * 12) + annual_total
          score        = get_waste_score(
              monthly_total, len(found_subs)
          )
          filled = "█" * score
          empty  = "░" * (10 - score)

          print(f"\n  {'─'*54}")
          print(f"  📋 SUBSCRIPTIONS: {len(found_subs)} found")
          print(f"  {'─'*54}")

          annual_subs  = [s for s in found_subs
                          if s["is_annual"]]
          monthly_subs = [s for s in found_subs
                          if not s["is_annual"]]

          if annual_subs:
              print(f"\n  📅 Annual:")
              for s in annual_subs:
                  tag   = "[actual]" if s["confirmed"] \
                          else "[estimate]"
                  equiv = f"≈₹{s['monthly_equiv']:,.0f}/mo"
                  print(f"     {s['name']:<28} "
                        f"₹{s['yearly_cost']:>8,.0f}/yr  "
                        f"{equiv}  {tag}")
          if monthly_subs:
              print(f"\n  📆 Monthly:")
              for s in monthly_subs:
                  tag = "[actual]" if s["confirmed"] \
                        else "[estimate]"
                  print(f"     {s['name']:<28} "
                        f"₹{s['monthly_equiv']:>7,.0f}/mo  {tag}")

          print(f"\n  {'─'*54}")
          print(f"  💸 Monthly total    ₹{monthly_total:>8,.0f}/mo")
          print(f"  📅 Annual total     ₹{annual_total:>8,.0f}/yr")
          print(f"  📊 TRUE yearly      ₹{true_yearly:>8,.0f}/yr")
          print(f"\n  📊 WASTE SCORE: {filled}{empty} "
                f"{score}/10  {score_label(score)}")
      else:
          print("\n  ✅ No subscriptions detected.")
          monthly_total = 0
          annual_total  = 0
          true_yearly   = 0

      # ── Spending Breakdown ────────────────────────────
      if grand_total > 0:
          print(f"\n  {'─'*54}")
          print(f"  💰 SPENDING BREAKDOWN")
          print(f"  {'─'*54}")
          for cat in sorted(
              categorised,
              key=lambda x: sum(
                  t["debit"] for t in categorised[x]),
              reverse=True
          ):
              total = sum(
                  t["debit"] for t in categorised[cat]
              )
              pct = (total / grand_total) * 100
              bar = "█" * max(1, int(pct / 5))
              print(f"  {cat:<30} ₹{total:>8,.0f} "
                    f" {pct:>5.1f}%  {bar}")
          if uncategorised:
              unk = sum(t["debit"] for t in uncategorised)
              pct = unk / grand_total * 100
              print(f"  {'❓ Unknown':<30} "
                    f"₹{unk:>8,.0f}  {pct:>5.1f}%")
          savings = unnecessary_total * 0.25
          print(f"\n  Total      ₹{grand_total:>8,.0f}")
          print(f"  ✅ Needed  ₹{necessary_total:>8,.0f}")
          print(f"  ⚠️  Wasted ₹{unnecessary_total:>8,.0f}")
          print(f"  💡 Cut 25% → ₹{savings:,.0f}/mo saved")
          # --- NEW FEATURE 2: SAVINGS POTENTIAL ---
      savings_potential = unnecessary_total * 0.25
      print(f"\n  💡 FINANCIAL TIP:")
      print(f"  If you reduce your non-essential spending by just 25%, you could save ₹{savings_potential:,.0f} every month!")
      print(f"  That is an extra ₹{savings_potential * 12:,.0f} in your pocket annually! 🚀")

      # ── Budget Alerts ─────────────────────────────────
      print(f"\n  {'─'*54}")
      print(f"  💳 BUDGET ALERTS")
      print(f"  {'─'*54}")
      for cat, budget in budgets.items():
          total_spent = sum(
              t["debit"] for t in categorised.get(cat, [])
          )
          avg_monthly = total_spent / months_count
          if avg_monthly == 0:
              continue
          pct      = (avg_monthly / budget * 100) \
                    if budget > 0 else 0
          diff     = avg_monthly - budget
          bar_fill = min(int(pct / 10), 10)
          bar      = "█" * bar_fill + "░" * (10 - bar_fill)
          status   = ("🔴 OVER" if pct > 100 else
                      "🟡 NEAR" if pct > 80 else "🟢 OK")
          print(f"\n  {cat}")
          print(f"  {bar}  {pct:.0f}%  {status}")
          print(f"  ₹{avg_monthly:,.0f}/mo vs "
                f"₹{budget:,.0f} budget  "
                f"{'Over' if diff>0 else 'Under'} "
                f"₹{abs(diff):,.0f}")

      print(f"\n  🔴 Over: {len(over_budget)}  "
            f"🟡 Near: {len(near_budget)}  "
            f"🟢 OK: {len(under_budget)}")

      # ── Monthly Report Card ───────────────────────────
      if len(seen_months) >= 2:
          all_cats = sorted(set(
              cat for m in monthly_summary.values()
              for cat in m
          ))
          col_w = 12
          print(f"\n  {'─'*54}")
          print(f"  📊 MONTHLY REPORT CARD")
          print(f"  {'─'*54}")
          print(f"  {', '.join(seen_months)}")
          header = f"\n  {'Category':<28}"
          for m in seen_months:
              header += f"{m:>{col_w}}"
          header += "   Trend"
          print(header)
          print(f"  {'─'*28}" +
                "─" * (col_w * len(seen_months) + 10))
          for cat in all_cats:
              row    = f"  {cat:<28}"
              values = []
              for m in seen_months:
                  val = monthly_summary[m].get(cat, 0)
                  values.append(val)
                  row += (f"₹{val:>9,.0f}  " if val > 0
                          else f"{'—':>10}  ")
              non_zero = [v for v in values if v > 0]
              if len(non_zero) >= 2:
                  pct   = ((non_zero[-1] - non_zero[-2])
                          / non_zero[-2] * 100)
                  trend = (f"📈 +{pct:.0f}%" if pct > 20
                          else f"📉 {pct:.0f}%" if pct < -20
                          else f"➡️  {pct:+.0f}%")
              else:
                  trend = "  —"
              print(f"{row}  {trend}")
          print(f"  {'─'*28}" +
                "─" * (col_w * len(seen_months) + 10))
          total_row = f"  {'💰 TOTAL':<28}"
          for m in seen_months:
              total_row += \
                  f"₹{monthly_totals.get(m,0):>9,.0f}  "
          print(total_row)
          if monthly_totals:
              best  = min(monthly_totals,
                          key=monthly_totals.get)
              worst = max(monthly_totals,
                          key=monthly_totals.get)
              avg_m = (sum(monthly_totals.values())
                      / len(monthly_totals))
              print(f"\n  🏆 Best:  {best} "
                    f"₹{monthly_totals[best]:,.0f}")
              print(f"  ⚠️  Worst: {worst} "
                    f"₹{monthly_totals[worst]:,.0f}")
              print(f"  📊 Avg:   ₹{avg_m:,.0f}/month")
              # --- NEW FEATURE 3: TOP 3 SPIKE DETECTOR ---
      if len(seen_months) >= 2:
          safe_cats = sorted(set(cat for m in monthly_summary.values() for cat in m))
          spikes = []
          for cat in safe_cats:
              vals = [(m, monthly_summary[m].get(cat, 0)) for m in seen_months]
              nz = [(m, v) for m, v in vals if v > 0]
              if len(nz) >= 2:
                  lm, lv = nz[-1]
                  pm, pv = nz[-2]
                  if pv > 0:
                      pct = (lv - pv) / pv * 100
                      if pct > 25:
                          spikes.append((cat, pm, pv, lm, lv, pct))

          if spikes:
              print(f"\n  🚨 SPENDING SPIKES DETECTED:")
              for cat, pm, pv, lm, lv, pct in sorted(spikes, key=lambda x: x[5], reverse=True)[:3]:
                  print(f"  - {cat}: Jumped {pct:.0f}% from {pm} to {lm}! (₹{pv:,.0f} ➡️ ₹{lv:,.0f})")

      # ── Forgotten Subscriptions ───────────────────────
      if found_subs:
          print(f"\n  {'─'*54}")
          print(f"  🔍 FORGOTTEN SUBSCRIPTION DETECTOR")
          print(f"  {'─'*54}")
          results    = []
          risk_order = {
              "high": 0, "medium": 1, "annual": 2,
              "low": 3, "unknown": 4
          }
          for sub in found_subs:
              if sub["is_annual"]:
                  results.append({**sub,
                      "count":  1,
                      "status": "📅 Annual — once/year",
                      "risk":   "annual"})
                  continue
              count      = 0
              name_words = [
                  w for w in sub["name"].upper().split()
                  if len(w) > 3
              ]
              for txn in transactions:
                  if any(w in txn["description"].upper()
                        for w in name_words):
                      count += 1
              if count == 0:
                  status, risk = "❓ Not detected", "unknown"
              elif count == 1:
                  status = "🔴 Possibly forgotten"
                  risk   = "high"
              elif count == 2:
                  status = "🟡 Monitor"
                  risk   = "medium"
              else:
                  status = f"🟢 Active ({count}x)"
                  risk   = "low"
              results.append({**sub,
                  "count": count,
                  "status": status,
                  "risk": risk})
          results.sort(key=lambda x: risk_order[x["risk"]])
          for r in results:
              if r["risk"] == "annual":
                  print(f"  📅 {r['name']:<28}"
                        f" ₹{r['yearly_cost']:>8,.0f}/yr")
              elif r["risk"] == "high":
                  print(f"  🔴 {r['name']:<28}"
                        f" ₹{r['monthly_equiv']:,.0f}/mo"
                        f" — {r['status']}")
              elif r["risk"] == "medium":
                  print(f"  🟡 {r['name']:<28}"
                        f" {r['status']}")
              else:
                  print(f"  🟢 {r['name']:<28}"
                        f" {r['status']}")
          forgotten_cost = sum(
              r["yearly_cost"] for r in results
              if r["risk"] == "high"
          )
          if forgotten_cost > 0:
              print(f"\n  ⚡ Cancel forgotten → "
                    f"save ₹{forgotten_cost:,.0f}/yr!")

      # ── Cancellation Guide ────────────────────────────
      if found_subs:
          print(f"\n  {'─'*54}")
          print(f"  ❌ CANCELLATION GUIDE")
          print(f"  {'─'*54}")
          print("\n  NUMBER or NAME. 'all' / 'done'\n")
          for i, s in enumerate(found_subs, 1):
              has  = any(k.lower() in s["name"].lower()
                        or s["name"].lower() in k.lower()
                        for k in CANCEL_GUIDE)
              tag  = "✅" if has else "🔍"
              freq = "annual" if s["is_annual"] else "monthly"
              print(f"  {i:>2}. {s['name']:<28} "
                    f"[{freq}]  {tag}")
          print()
          while True:
              user_input = input(
                  "  Cancel which? (number/name/all/done): "
              ).strip()
              if user_input.lower() == "done":
                  print("\n  ✅ Done.")
                  break
              if user_input.lower() == "all":
                  for s in found_subs:
                      guide = next(
                          (v for k, v in CANCEL_GUIDE.items()
                          if k.lower() in s["name"].lower()
                          or s["name"].lower()
                          in k.lower()), None)
                      if guide:
                          cost = (
                              f"₹{s['yearly_cost']:,.0f}/yr"
                              if s["is_annual"]
                              else
                              f"₹{s['monthly_equiv']:,.0f}/mo"
                          )
                          print(f"\n  ── {s['name']}"
                                f" ({cost}) ──")
                          for step in guide:
                              print(f"     {step}")
                  continue
              matched = None
              if user_input.isdigit():
                  idx = int(user_input) - 1
                  if 0 <= idx < len(found_subs):
                      matched = found_subs[idx]
                  else:
                      print(f"  ⚠️ Enter 1-{len(found_subs)}")
                      continue
              else:
                  for s in found_subs:
                      if user_input.lower() \
                              in s["name"].lower():
                          matched = s
                          break
              if matched:
                  guide = next(
                      (v for k, v in CANCEL_GUIDE.items()
                      if k.lower() in matched["name"].lower()
                      or matched["name"].lower()
                      in k.lower()), None)
                  cost = (
                      f"₹{matched['yearly_cost']:,.0f}/yr"
                      if matched["is_annual"]
                      else
                      f"₹{matched['monthly_equiv']:,.0f}/mo"
                  )
                  print(f"\n  ── {matched['name']}"
                        f" ({cost}) ──")
                  if guide:
                      for step in guide:
                          print(f"  {step}")
                      print(f"\n  💰 Save "
                            f"₹{matched['yearly_cost']:,.0f}/yr")
                  else:
                      print(f"  Search: "
                            f"'{matched['name']} cancel India'")
                  print()
              else:
                  print(f"  ⚠️ Not found.")

      # ── WhatsApp Share ────────────────────────────────
      if found_subs:
          avg = (sum(monthly_totals.values())
                / len(monthly_totals)
                if monthly_totals else 0)
          print(f"""
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    💬 SHARE ON WHATSAPP

    🛡️ *Legasafe Report*
    My Financial Health Score: {total_score}/100 {health_label(total_score)}
    • {len(found_subs)} subscriptions | ₹{true_yearly:,.0f}/yr
    • Avg monthly spend: ₹{avg:,.0f}
    • {len(over_budget)} categories over budget
    {f'• Forgotten subs: ₹{sum(s["yearly_cost"] for s in forgotten_subs):,.0f}/yr wasted 😱' if forgotten_subs else '• No forgotten subs ✅'}

    What's your score?
    Try free 👉 aksharrajput4-netizen.github.io/Legasafe
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🔒 Zero data uploaded. 100% local. Always.
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          """)

        # ════════════════════════════════════════════════════════════
      #  VISUALIZATION ENGINE (PIE CHART) - THE REAL CATEGORY FIX
      # ════════════════════════════════════════════════════════════
      print("\n  [CHART] Generating Spending Category Chart...")

      import matplotlib.pyplot as plt

      # 1. Mini-categorizer to group transactions based on keywords
      def assign_category(description):
          desc = description.lower()
          if any(word in desc for word in ["rent", "jio", "airtel", "fiber"]):
              return "Bills & Utilities"
          if any(word in desc for word in ["netflix", "steam", "playstation", "spotify", "amazon", "google", "gaming"]):
              return "Gaming & Entertainment"
          if any(word in desc for word in ["pathlab", "pharmacy", "chemist", "clinic", "medical"]):
              return "Health & Medical"
          if any(word in desc for word in ["dhaba", "chai", "sweets", "kachori", "chaat", "bikanerwala", "karim", "tikki", "dairy", "store", "cafe"]):
              return "Food & Dining"
          if any(word in desc for word in ["ola", "uber", "irctc", "metro", "auto", "rickshaw", "travel", "cab"]):
              return "Transport"
          return "Other"

      # 2. Tally up the money using the new categorizer
      spending_data = {}
      for t in transactions:
          cat = assign_category(t["description"])
          spending_data[cat] = spending_data.get(cat, 0) + t["debit"]

      # 3. Sort from largest category to smallest
      sorted_spending = sorted(spending_data.items(), key=lambda x: x[1], reverse=True)

      labels = [item[0] for item in sorted_spending]
      sizes = [item[1] for item in sorted_spending]

      # 4. Draw the Chart
      plt.figure(figsize=(8, 6))
      plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
      plt.title("Spending by Category", size=16, fontweight="bold")
      plt.show()

      # ════════════════════════════════════════════════════════════
      #  EXCEL EXPORT ENGINE - EMOJI & OPENPYXL FIX
      # ════════════════════════════════════════════════════════════
      print()
      while True:
          export_choice = input("  💾 Download full transaction history as Excel? (Y/N): ").strip().upper()
          if export_choice in ["Y", "N"]:
              break
          print("  ⚠️ Please type exactly 'Y' for Yes or 'N' for No.")

      if export_choice == "Y":
          import pandas as pd

          formatted_data = []
          for t in transactions:
              sub_type = "Yearly" if t.get("is_annual") else "Standard"
              formatted_data.append({
                  "Month": t.get("month", ""),
                  "Category": t.get("category", ""),
                  "Description": t.get("description", ""),
                  "Amount (INR)": t.get("debit", 0),
                  "Subscription Type": sub_type
              })

          df = pd.DataFrame(formatted_data)
          excel_filename = "Legasafe_Transactions.xlsx"

          # Explicitly force openpyxl to prevent crashes and preserve emojis
          try:
                df.to_excel(excel_filename, index=False, engine='openpyxl')
                # (The import line that was here is now deleted!)
                files.download(excel_filename)
                print("\n  [+] Professional Excel file generated! Check your browser downloads.")
          except ImportError:
                print("\n  [X] Error: 'openpyxl' is missing. Run '!pip install openpyxl' in a new Colab cell to fix.")
      else:
          print("\n  ✅ Export skipped.")

run_legasafe()
