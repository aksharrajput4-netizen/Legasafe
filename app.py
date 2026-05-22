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
        st.write(data)

    st.success("Analysis Complete.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"₹{data['total_spent']:,.0f}")
    col2.metric("Transactions", data['transaction_count'])
    col3.metric("Active Subs", len(data['subscriptions_found']))

    st.divider()

    st.subheader("Where did your money go?")
    if data['category_breakdown']:
        st.bar_chart(data['category_breakdown'])

    if data['subscriptions_found']:
        st.subheader("🕵️ Subscription Radar")
        for sub in data['subscriptions_found']:
            st.error(f"**{sub['name']}**: ₹{sub['cost']} / month")
