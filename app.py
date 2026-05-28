import streamlit as st
import pandas as pd
import io
from legasafe_engine import process_pdf

st.set_page_config(page_title="Legasafe", page_icon="🛡️", layout="centered")

# --- Custom CSS ---
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stApp { background-color: #0f1117; }
    h1 { color: #ffffff; font-family: 'Georgia', serif; }
    .metric-card {
        background: #1a1d27;
        border: 1px solid #2d3147;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .section-header {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    .sub-row {
        background: #1a1d27;
        border-left: 3px solid #3b82f6;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        margin: 6px 0;
        color: #e2e8f0;
    }
    .health-good { color: #22c55e; font-size: 2rem; font-weight: 800; }
    .health-mid  { color: #f59e0b; font-size: 2rem; font-weight: 800; }
    .health-bad  { color: #ef4444; font-size: 2rem; font-weight: 800; }
    .badge {
        display: inline-block;
        background: #3b82f6;
        color: white;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("# 🛡️ Legasafe")
st.markdown("**Find every rupee. Know every subscription. Zero data uploaded.**")
st.divider()

# --- File Upload ---
uploaded_file = st.file_uploader(
    "Drop your Bank Statement PDF here",
    type="pdf",
    help="Works with SBI, HDFC, ICICI, Axis, Kotak and all major Indian banks. Nothing is sent to any server."
)

if uploaded_file:
    with st.spinner("Scanning your statement..."):
        data = process_pdf(uploaded_file)

    # ── 1. Top Metrics ──────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spent", f"₹{data['total_spent']:,.0f}")
    col2.metric("Transactions", data['transaction_count'])
    col3.metric("Active Subs", len(data['subscriptions_found']))

    score = data['health_score']
    score_color = "health-good" if score >= 70 else ("health-mid" if score >= 40 else "health-bad")
    col4.markdown(f"**Health Score**")
    col4.markdown(f'<span class="{score_color}">{score}/100</span>', unsafe_allow_html=True)

    st.divider()

    # ── 2. Budget Tracker ───────────────────────────────────────────
    st.subheader("🎯 Budget Tracker")
    user_budget = st.number_input(
        "Monthly budget target (₹):",
        min_value=0, value=50000, step=1000
    )
    spent = data['total_spent']
    if spent > user_budget:
        st.error(f"⚠️ Over budget by ₹{spent - user_budget:,.0f}")
    else:
        st.success(f"✅ Under budget by ₹{user_budget - spent:,.0f} — well done!")

    # ── 3. Subscription Radar ───────────────────────────────────────
    subs = data.get('subscriptions_found', [])
    if subs:
        st.divider()
        st.subheader(f"📡 Subscription Radar  ({len(subs)} found)")
        sub_rows = []
        for sub in subs:
            freq = sub.get('frequency', 'monthly')
            yearly = sub['amount'] * 12 if freq == 'monthly' else sub['amount']
            badge = "Annual" if freq == 'annual' else "Monthly"
            st.markdown(
                f'<div class="sub-row">• <b>{sub["name"]}</b> — '
                f'₹{sub["amount"]:,.0f} <span style="color:#94a3b8">({badge})</span>'
                f' &nbsp;|&nbsp; <span style="color:#f59e0b">₹{yearly:,.0f}/yr</span></div>',
                unsafe_allow_html=True
            )
            sub_rows.append({
                "Service": sub["name"],
                "Amount (₹)": sub["amount"],
                "Frequency": badge,
                "Yearly Cost (₹)": yearly
            })

        total_yearly = sum(r["Yearly Cost (₹)"] for r in sub_rows)
        st.markdown(f"**Total subscription burn: ₹{total_yearly:,.0f}/year**")

    # ── 4. Category Breakdown ───────────────────────────────────────
    categories = data.get('categories', {})
    if categories:
        st.divider()
        st.subheader("🗂️ Spending by Category")
        cat_df = pd.DataFrame(
            list(categories.items()), columns=["Category", "Amount (₹)"]
        ).sort_values("Amount (₹)", ascending=False)
        st.bar_chart(cat_df.set_index("Category"))

    # ── 5. Monthly Trends ───────────────────────────────────────────
    monthly = data.get('monthly_totals', {})
    if monthly:
        st.divider()
        st.subheader("📈 Monthly Spending Trend")
        trend_df = pd.DataFrame(
            list(monthly.items()), columns=["Month", "Spent (₹)"]
        )
        st.line_chart(trend_df.set_index("Month"))

    # ── 6. CSV Export ───────────────────────────────────────────────
    st.divider()
    st.subheader("⬇️ Export Your Data")

    transactions = data.get('transactions', [])
    if transactions:
        tx_df = pd.DataFrame(transactions)

        # Full transactions CSV
        csv_tx = tx_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download All Transactions (CSV)",
            data=csv_tx,
            file_name="legasafe_transactions.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Subscriptions CSV
    if subs:
        subs_df = pd.DataFrame(sub_rows)
        csv_subs = subs_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📋 Download Subscriptions List (CSV)",
            data=csv_subs,
            file_name="legasafe_subscriptions.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Summary CSV
    summary = {
        "Metric": ["Total Spent", "Transactions", "Active Subscriptions",
                   "Health Score", "Yearly Subscription Cost"],
        "Value": [
            f"₹{data['total_spent']:,.0f}",
            data['transaction_count'],
            len(subs),
            f"{score}/100",
            f"₹{sum(r['Yearly Cost (₹)'] for r in sub_rows) if subs else 0:,.0f}"
        ]
    }
    csv_summary = pd.DataFrame(summary).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Download Summary Report (CSV)",
        data=csv_summary,
        file_name="legasafe_summary.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()
    st.caption("🔒 Your data was never uploaded. All processing happened locally on your device.")

else:
    # Empty state — show what to expect
    st.info("Upload your bank statement PDF above to get started. No account needed.")
    with st.expander("✅ Supported banks"):
        st.markdown("""
        - SBI (State Bank of India)
        - HDFC Bank
        - ICICI Bank
        - Axis Bank
        - Kotak Mahindra Bank
        - Most other Indian banks
        """)
    with st.expander("🔒 Privacy — how it works"):
        st.markdown("""
        Your PDF is read entirely within this browser session.
        Nothing is sent to any server. Nothing is stored.
        When you close this tab, everything is gone.
        """)
