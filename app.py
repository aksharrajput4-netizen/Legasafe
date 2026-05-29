import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from legasafe_engine import process_pdf

st.set_page_config(page_title="Legasafe", page_icon="🛡️", layout="centered")

# ── Brand colors ─────────────────────────────────────────────────────────────
GOLD       = "#C9A84C"
GOLD_LIGHT = "#E8C96A"
GOLD_DIM   = "#8A6F2E"
BG         = "#0a0b0f"
SURFACE    = "#111318"
BORDER     = "#1e2230"
TEXT       = "#f0ead8"
TEXT_MUTED = "#7a7060"
GREEN      = "#4ade80"
AMBER      = "#f59e0b"
RED        = "#ef4444"

# ── Plotly dark theme ─────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(color=TEXT, family="DM Sans, sans-serif", size=13),
    margin=dict(l=16, r=16, t=32, b=16),
    xaxis=dict(gridcolor=BORDER, linecolor=BORDER,
               tickfont=dict(color=TEXT_MUTED), title_font=dict(color=TEXT_MUTED)),
    yaxis=dict(gridcolor=BORDER, linecolor=BORDER,
               tickfont=dict(color=TEXT_MUTED), title_font=dict(color=TEXT_MUTED)),
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp, .main, section.main > div {{ background-color: {BG} !important; }}
  h1, h2, h3 {{ color: {TEXT} !important; }}
  hr {{ border-color: {BORDER} !important; }}
  [data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-size: 0.8rem; }}
  [data-testid="stMetricValue"] {{ color: {GOLD} !important; font-size: 1.6rem !important; font-weight: 700 !important; }}
  [data-testid="stFileUploader"] {{
    background: {SURFACE}; border: 1px dashed {BORDER}; border-radius: 12px; padding: 8px;
  }}
  [data-testid="stNumberInput"] input {{
    background: {SURFACE} !important; color: {TEXT} !important; border-color: {BORDER} !important;
  }}
  .stDownloadButton > button {{
    background: linear-gradient(135deg, {GOLD}, {GOLD_DIM}) !important;
    color: #0a0b0f !important; font-weight: 700 !important;
    border: none !important; border-radius: 8px !important;
    padding: 10px 20px !important; width: 100% !important;
  }}
  .stDownloadButton > button:hover {{ opacity: 0.85 !important; }}
  [data-testid="stExpander"] {{
    background: {SURFACE} !important; border: 1px solid {BORDER} !important; border-radius: 10px !important;
  }}
  .stAlert {{ border-radius: 10px !important; }}
  .sub-card {{
    background: {SURFACE}; border: 1px solid {BORDER};
    border-left: 3px solid {GOLD}; border-radius: 0 10px 10px 0;
    padding: 10px 16px; margin: 6px 0; color: {TEXT}; font-size: 0.92rem;
  }}
  .sub-card b {{ color: {GOLD_LIGHT}; }}
  .sub-yearly {{ color: {AMBER}; font-weight: 600; }}
  .score-good {{ color: {GREEN};  font-size: 2.2rem; font-weight: 800; line-height: 1; }}
  .score-mid  {{ color: {AMBER};  font-size: 2.2rem; font-weight: 800; line-height: 1; }}
  .score-bad  {{ color: {RED};    font-size: 2.2rem; font-weight: 800; line-height: 1; }}
  .score-label {{ color: {TEXT_MUTED}; font-size: 0.78rem; margin-bottom: 4px; }}
  .stCaption {{ color: {TEXT_MUTED} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"<h1 style='color:{GOLD};font-family:Georgia,serif;letter-spacing:2px;'>🛡️ LEGASAFE</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:{TEXT_MUTED};margin-top:-12px;'>Find every rupee. Know every subscription. Zero data uploaded.</p>", unsafe_allow_html=True)
st.divider()

# ── Frequency resolver ────────────────────────────────────────────────────────
def resolve_frequency(sub):
    name = sub.get('name', '').lower()
    freq = sub.get('frequency', '').lower().strip()

    if any(x in name for x in ['annual', 'yearly', '/year', 'per year']):
        return 'Annual', 1
    if any(x in name for x in ['6-month', '6month', 'half-year', 'semi', 'biannual']):
        return '6-Month', 2
    if any(x in name for x in ['3-month', '3month', 'quarter', 'quarterly']):
        return 'Quarterly', 4

    if freq in ('annual', 'annually', 'yearly', 'year'):
        return 'Annual', 1
    if freq in ('semi-annual', '6-month', '6month', 'half-yearly', 'biannual'):
        return '6-Month', 2
    if freq in ('quarterly', '3-month', '3month', 'quarter'):
        return 'Quarterly', 4

    return 'Monthly', 12

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "📄 Drop your Bank Statement PDF here",
    type="pdf",
    help="SBI, HDFC, ICICI, Axis, Kotak and all major Indian banks. Nothing sent to any server."
)

if uploaded_file:
    with st.spinner("Scanning your statement..."):
        data = process_pdf(uploaded_file)

    subs    = data.get('subscriptions_found', [])
    score   = data.get('health_score', 0)
    cats    = data.get('categories', {})
    monthly = data.get('monthly_totals', {})
    txns    = data.get('transactions', [])

    # ── 1. Top Metrics ────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spent",  f"₹{data['total_spent']:,.0f}")
    col2.metric("Transactions", data['transaction_count'])
    col3.metric("Active Subs",  len(subs))
    score_cls = "score-good" if score >= 70 else ("score-mid" if score >= 40 else "score-bad")
    col4.markdown(
        f"<div class='score-label'>Health Score</div>"
        f"<div class='{score_cls}'>{score}<span style='font-size:1rem'>/100</span></div>",
        unsafe_allow_html=True
    )
    st.divider()

    # ── 2. Budget Tracker ─────────────────────────────────────────────────────
    st.subheader("🎯 Budget Tracker")
    user_budget = st.number_input("Monthly budget target (₹):", min_value=0, value=50000, step=1000)
    spent = data['total_spent']
    if spent > user_budget:
        over = spent - user_budget
        pct  = int(over / user_budget * 100)
        st.error(f"⚠️ Over budget by ₹{over:,.0f} ({pct}% over)")
    else:
        left = user_budget - spent
        pct  = int(left / user_budget * 100)
        st.success(f"✅ Under budget — ₹{left:,.0f} remaining ({pct}% of budget left)")

    # ── 3. Subscription Radar ─────────────────────────────────────────────────
    sub_rows = []
    if subs:
        st.divider()
        st.subheader(f"📡 Subscription Radar — {len(subs)} found")
        for sub in subs:
            badge, multiplier = resolve_frequency(sub)
            yearly = sub['amount'] * multiplier
            st.markdown(
                f'<div class="sub-card">'
                f'<b>{sub["name"]}</b>'
                f'<span style="color:{TEXT_MUTED}"> · {badge}</span>'
                f' &nbsp;·&nbsp; ₹{sub["amount"]:,.0f}'
                f' &nbsp;|&nbsp; <span class="sub-yearly">₹{yearly:,.0f}/yr</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            sub_rows.append({
                "Service":        sub["name"],
                "Amount (₹)":     sub["amount"],
                "Frequency":      badge,
                "Yearly Cost (₹)": yearly
            })
        total_yearly = sum(r["Yearly Cost (₹)"] for r in sub_rows)
        st.markdown(
            f"<p style='color:{AMBER};font-weight:700;margin-top:10px;'>"
            f"Total subscription burn: ₹{total_yearly:,.0f}/year</p>",
            unsafe_allow_html=True
        )

    # ── 4. Category Breakdown ─────────────────────────────────────────────────
    if cats:
        st.divider()
        st.subheader("🗂️ Spending by Category")
        cat_df = (
            pd.DataFrame(list(cats.items()), columns=["Category", "Amount"])
            .sort_values("Amount", ascending=True)
        )
        n = len(cat_df)
        colors = [
            f"rgba(201,168,76,{0.35 + 0.65 * (i / max(n-1, 1))})"
            for i in range(n)
        ]
        fig_cat = go.Figure(go.Bar(
            x=cat_df["Amount"],
            y=cat_df["Category"],
            orientation='h',
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"₹{v:,.0f}" for v in cat_df["Amount"]],
            textposition='outside',
            textfont=dict(color=TEXT, size=12),
            hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
        ))
        fig_cat.update_layout(
            **CHART_LAYOUT,
            height=max(280, n * 42),
            xaxis_title="Amount (₹)",
            yaxis_title=None,
            showlegend=False,
        )
        fig_cat.update_xaxes(tickprefix="₹", tickformat=",")
        st.plotly_chart(fig_cat, use_container_width=True)

    # ── 5. Monthly Trend ──────────────────────────────────────────────────────
    if monthly:
        st.divider()
        st.subheader("📈 Monthly Spending Trend")
        trend_df = pd.DataFrame(list(monthly.items()), columns=["Month", "Spent"])
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_df["Month"],
            y=trend_df["Spent"],
            mode='lines+markers',
            line=dict(color=GOLD, width=2.5),
            marker=dict(color=GOLD_LIGHT, size=7, line=dict(color=BG, width=2)),
            fill='tozeroy',
            fillcolor="rgba(201,168,76,0.08)",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
            name="Spending",
        ))
        fig_trend.update_layout(
            **CHART_LAYOUT,
            height=300,
            yaxis_title="Amount (₹)",
            xaxis_title=None,
            showlegend=False,
        )
        fig_trend.update_yaxes(tickprefix="₹", tickformat=",")
        st.plotly_chart(fig_trend, use_container_width=True)

    # ── 6. CSV Export ─────────────────────────────────────────────────────────
    st.divider()
    st.subheader("⬇️ Export Your Data")
    ecol1, ecol2, ecol3 = st.columns(3)

    if txns:
        tx_csv = pd.DataFrame(txns).to_csv(index=False).encode('utf-8')
        ecol1.download_button("📄 All Transactions", tx_csv,
                              "legasafe_transactions.csv", "text/csv", use_container_width=True)

    if sub_rows:
        subs_csv = pd.DataFrame(sub_rows).to_csv(index=False).encode('utf-8')
        ecol2.download_button("📋 Subscriptions", subs_csv,
                              "legasafe_subscriptions.csv", "text/csv", use_container_width=True)

    summary_csv = pd.DataFrame({
        "Metric": ["Total Spent", "Transactions", "Active Subscriptions",
                   "Health Score", "Yearly Subscription Cost"],
        "Value": [
            f"₹{data['total_spent']:,.0f}",
            data['transaction_count'],
            len(subs),
            f"{score}/100",
            f"₹{sum(r['Yearly Cost (₹)'] for r in sub_rows) if sub_rows else 0:,.0f}"
        ]
    }).to_csv(index=False).encode('utf-8')
    ecol3.download_button("📊 Summary Report", summary_csv,
                          "legasafe_summary.csv", "text/csv", use_container_width=True)

    st.divider()
    st.caption("🔒 Your data was never uploaded. All processing happened locally on your device.")

else:
    # ── Empty state ───────────────────────────────────────────────────────────
    st.markdown(
        f"<p style='color:{TEXT_MUTED};'>Upload your bank statement PDF above to get started. No account needed.</p>",
        unsafe_allow_html=True
    )
    with st.expander("✅ Supported banks"):
        st.markdown("""
        SBI · HDFC Bank · ICICI Bank · Axis Bank · Kotak Mahindra Bank ·
        Bank of Baroda · Punjab National Bank · Canara Bank · and more
        """)
    with st.expander("🔒 How privacy works"):
        st.markdown("""
        Your PDF is processed entirely in your browser session.
        Nothing is sent to any server. Nothing is stored.
        When you close this tab, everything is gone.
        """)
