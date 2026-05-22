import streamlit as st
import pandas as pd
from legasafe_engine import process_pdf

st.set_page_config(page_title="Legasafe MVP", page_icon="🛡️", layout="centered")

st.title("🛡️ Legasafe")
st.markdown("**Financial clarity, processed instantly.**")

uploaded_file = st.file_uploader("Drop your Bank Statement (PDF) here", type="pdf")

if uploaded_file:
    with st.spinner('Analyzing your digital footprint...'):
        data = process_pdf(uploaded_file)
       

 # 1. Expand to 4 columns to make room for the Health Score
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Spent", f"₹{data['total_spent']:,.0f}")
        col2.metric("Transactions", data['transaction_count'])
        col3.metric("Active Subs", len(data['subscriptions_found']))
        col4.metric("Health Score", f"{data['health_score']}/100")

        # 2. Add the Budget Alert UI below the metrics
        st.divider()
        st.subheader("🎯 Budget Tracker")
        
        user_budget = st.number_input("Enter your monthly budget target (₹):", min_value=0, value=50000, step=1000)

        if data['total_spent'] > user_budget:
            overage = data['total_spent'] - user_budget
            st.error(f"⚠️ You are over budget by ₹{overage:,.0f}!")
        else:
            savings = user_budget - data['total_spent']
            st.success(f"✅ You are under budget by ₹{savings:,.0f}. Great job!")
            
        # 3. Bring back your Subscription Radar
        if data['subscriptions_found']:
            st.divider()
            st.subheader("📡 Subscription Radar")
            for sub in data['subscriptions_found']:
                st.write(f"• **{sub['name']}**: ₹{sub['amount']}")
