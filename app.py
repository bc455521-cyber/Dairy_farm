import os
import pandas as pd
import streamlit as st
from datetime import datetime

# File to store local session data safely
DATA_FILE = "dairy_sales_records.csv"

PRODUCTS = [
    "Milk", "Curd", "Ghee", "Buttermilk", 
    "Sonpapidi", "Badam Milk", "Flavored Milk", 
    "Basundhi", "Paneer"
]

if 'sales_df' not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.sales_df = pd.read_csv(DATA_FILE)
    else:
        st.session_state.sales_df = pd.DataFrame(
            columns=["Purchase Date", "Customer Name", "Item", "Quantity", "Rate Per Unit", "Total Price"]
        )

st.set_page_config(page_title="Dairy Tracker", page_icon="🥛", layout="centered")

# Mobile CSS styling to make elements larger and tap-friendly
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 50px; font-size: 20px; background-color: #4CAF50; color: white;}
    div[data-testid="stMetricValue"] { font-size: 28px; color: #2E7D32; }
    </style>
""", unsafe_allow_html=True)

st.title("🥛 My Dairy Shop")

# Mobile friendly input form
with st.form("mobile_sales_form", clear_on_submit=True):
    p_date = st.date_input("Purchase Date", datetime.now())
    cust_name = st.text_input("Customer Name", placeholder="e.g. Ramesh")
    chosen_item = st.selectbox("Select Item", PRODUCTS)
    qty = st.number_input("Quantity", min_value=0.0, step=1.0, value=0.0)
    custom_rate = st.number_input("Rate Per Unit (₹)", min_value=0.0, step=1.0, value=0.0)
    
    calculated_total = qty * custom_rate
    st.write(f"### Subtotal: ₹{calculated_total:,.2f}")
    
    submit = st.form_submit_button("💾 Save Order")

if submit:
    if not cust_name.strip() or qty <= 0 or custom_rate <= 0:
        st.error("దయచేసి అన్ని వివరాలను సరిగ్గా పూరించండి.")
    else:
        new_entry = {
            "Purchase Date": p_date.strftime("%Y-%m-%d"),
            "Customer Name": cust_name.strip(),
            "Item": chosen_item,
            "Quantity": qty,
            "Rate Per Unit": custom_rate,
            "Total Price": calculated_total
        }
        st.session_state.sales_df = pd.concat([st.session_state.sales_df, pd.DataFrame([new_entry])], ignore_index=True)
        st.session_state.sales_df.to_csv(DATA_FILE, index=False)
        st.success("విజయవంతంగా సేవ్ చేయబడింది!")

st.markdown("---")
st.subheader("📊 Sales History")

if not st.session_state.sales_df.empty:
    st.metric("Total Business Revenue", f"₹{st.session_state.sales_df['Total Price'].sum():,.2f}")
    st.dataframe(st.session_state.sales_df.sort_index(ascending=False), use_container_width=True)
    
    # Simple backup export option
    csv_data = st.session_state.sales_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export CSV Data", csv_data, "dairy_sales.csv", "text/csv")
else:
    st.info("ఈరోజు ఎలాంటి రికార్డులు లేవు.")
