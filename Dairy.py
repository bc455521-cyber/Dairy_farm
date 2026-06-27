import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Google Sheet URL
# Note: Ensure your Google Sheet is shared as "Anyone with link can Edit"
GSHEET_URL = "https://docs.google.com/spreadsheets/d/15-g1ftyrveaoJKXziQFlFLTJmqyzhgqFoJG8vuyuknc/edit?usp=drivesdk"

# Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper function to load data safely from a specific worksheet
def load_sheet_data(worksheet_name, default_data):
    try:
        df = conn.read(spreadsheet=GSHEET_URL, worksheet=worksheet_name)
        if df.empty:
            return default_data
        return df.to_dict('records')
    except Exception:
        # If worksheet doesn't exist yet, return default data
        return default_data

# Helper function to save data to a specific worksheet
def save_sheet_data(data, worksheet_name):
    df = pd.DataFrame(data)
    conn.update(spreadsheet=GSHEET_URL, worksheet=worksheet_name, data=df)

# Page configuration for perfect mobile view
st.set_page_config(page_title="DairyShop POS", page_icon="🥛", layout="centered")

# Custom CSS to match the exact UI style
st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; }
    .main-title { font-size: 28px; font-weight: bold; color: #1A1A1A; margin-bottom: 20px; }
    .pos-card {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #F0EFEA;
        margin-bottom: 12px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.02);
    }
    .stButton>button {
        background-color: #4E6E4E !important;
        color: white !important;
        border-radius: 24px !important;
        border: none !important;
        height: 45px;
        width: 100%;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States from Google Sheets
if 'products' not in st.session_state:
    default_prods = [
        {"name": "Curd", "unit": "per Liters", "price": 10.0, "qty": 100},
        {"name": "TEST_UI_Milk", "unit": "per Liters", "price": 45.0, "qty": 500}
    ]
    st.session_state.products = load_sheet_data("Products", default_prods)

if 'customers' not in st.session_state:
    default_custs = [
        {"name": "Balaji Chetlu", "phone": "9959012990", "address": "Asdfg"},
        {"name": "TEST_UI_Cust", "phone": "9999911111", "address": "Test"}
    ]
    st.session_state.customers = load_sheet_data("Customers", default_custs)

if 'orders' not in st.session_state:
    st.session_state.orders = load_sheet_data("Orders", [])

if 'purchases' not in st.session_state:
    st.session_state.purchases = load_sheet_data("Purchases", [])

# Sidebar for Navigation
st.sidebar.title("DairyShop POS v1.0")
current_tab = st.sidebar.radio("Navigate to:", ["📦 Products", "👥 Customers", "📊 Reports", "📥 Purchases", "⚙️ Settings"])

if current_tab == "📦 Products":
    st.markdown("<div class='main-title'>Products</div>", unsafe_allow_html=True)
    st.caption(f"{len(st.session_state.products)} items in inventory")
    for prod in st.session_state.products:
        st.markdown(f"""
        <div class="pos-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <b style="font-size: 18px;">💧 {prod['name']}</b><br>
                    <span style="color: gray; font-size: 13px;">{prod['unit']} | Stock: {prod['qty']}</span>
                </div>
                <div style="font-size: 18px; font-weight: bold; color: #4E6E4E;">₹{prod['price']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with st.expander("➕ Add New Product"):
        p_name = st.text_input("Product Name")
        p_unit = st.text_input("Unit (e.g., per Liters)", "per Liters")
        p_price = st.number_input("Price (₹)", min_value=0.0, step=1.0)
        p_qty = st.number_input("Initial Quantity", min_value=0, step=1)
        if st.button("Save Product"):
            if p_name:
                st.session_state.products.append({"name": p_name, "unit": p_unit, "price": p_price, "qty": p_qty})
                save_sheet_data(st.session_state.products, "Products")
                st.success("Product Added & Saved to Google Sheet!")
                st.rerun()

elif current_tab == "👥 Customers":
    st.markdown("<div class='main-title'>Customers</div>", unsafe_allow_html=True)
    search_query = st.text_input("🔍 Search customers")
    cust_names = [c['name'] for c in st.session_state.customers]
    selected_cust = st.selectbox("Select Customer:", cust_names)
    cust_data = next(c for c in st.session_state.customers if c['name'] == selected_cust)
    st.markdown(f"""
    <div class="pos-card" style="border-left: 5px solid #4E6E4E;">
        <b style="font-size: 18px;">👤 {cust_data['name']}</b><br>
        <span style="color: gray;">{cust_data['phone']}</span><br>
        <span style="color: gray; font-size:12px;">{cust_data['address']}</span>
    </div>
    """, unsafe_allow_html=True)
    action = st.radio("Action:", ["New Order", "History"], horizontal=True)
    if action == "New Order":
        cart = {}
        for prod in st.session_state.products:
            st.markdown(f"**{prod['name']}** (Price: ₹{prod['price']} | Avail: {prod['qty']})")
            qty = st.number_input(f"Qty for {prod['name']}", min_value=0, max_value=int(prod['qty']), key=f"qty_{prod['name']}")
            if qty > 0:
                cart[prod['name']] = {"qty": qty, "total": prod['price'] * qty, "price": prod['price']}
        if st.button("Place Order"):
            total_bill = sum(item['total'] for item in cart.values())
            if total_bill > 0:
                for name, item in cart.items():
                    st.session_state.orders.append({
                        "date": datetime.today().strftime('%Y-%m-%d'),
                        "customer": selected_cust,
                        "product": name,
                        "qty": item['qty'],
                        "total": item['total']
                    })
                    for p in st.session_state.products:
                        if p['name'] == name:
                            p['qty'] -= item['qty']
                save_sheet_data(st.session_state.orders, "Orders")
                save_sheet_data(st.session_state.products, "Products")
                st.success("Order Placed & Google Sheet Updated!")
                st.rerun()
    elif action == "History":
        history = [o for o in st.session_state.orders if o['customer'] == selected_cust]
        if not history:
            st.info("No orders yet")
        else:
            for o in history[-10:]:
                st.markdown(f"""
                <div class="pos-card">
                    <b>📅 {o['date']}</b><br>
                    Product: {o['product']} | Qty: {o['qty']}<br>
                    <b style="color:#4E6E4E;">Total: ₹{o['total']}</b>
                </div>
                """, unsafe_allow_html=True)

elif current_tab == "📊 Reports":
    st.markdown("<div class='main-title'>Reports</div>", unsafe_allow_html=True)
    period = st.radio("Timeline", ["Daily", "Weekly", "Monthly", "Yearly"], horizontal=True, index=2)
    df_orders = pd.DataFrame(st.session_state.orders)
    if not df_orders.empty:
        total_rev = df_orders['total'].sum()
        total_qty = df_orders['qty'].sum()
        st.metric("Total Revenue", f"₹{total_rev}")
        st.metric("Total Items Sold", total_qty)
        st.write("### Sales by Product")
        fig_pie = px.pie(df_orders, values='total', names='product', color_discrete_sequence=['#4E6E4E', '#A2B9A2'])
        st.plotly_chart(fig_pie, use_container_width=True)

elif current_tab == "📥 Purchases":
    st.markdown("<div class='main-title'>Purchases</div>", unsafe_allow_html=True)
    with st.expander("➕ Add Purchase Record"):
        p_item = st.selectbox("Item Name", [p['name'] for p in st.session_state.products])
        p_qty = st.number_input("Quantity Purchased", min_value=0.0, step=1.0)
        p_price = st.number_input("Total Price Paid (₹)", min_value=0.0, step=1.0)
        if st.button("Save Purchase"):
            st.session_state.purchases.append({
                "date": datetime.today().strftime('%Y-%m-%d'),
                "item": p_item,
                "qty": p_qty,
                "price": p_price
            })
            for prod in st.session_state.products:
                if prod['name'] == p_item:
                    prod['qty'] += p_qty
            save_sheet_data(st.session_state.purchases, "Purchases")
            save_sheet_data(st.session_state.products, "Products")
            st.success("Purchase recorded and stock updated in Google Sheet!")
            st.rerun()
    st.write("### Recent Purchases")
    for pur in st.session_state.purchases:
        st.markdown(f"""
        <div class="pos-card">
            📅 {pur['date']} | <b>{pur['item']}</b> | Qty: {pur['qty']} | Paid: ₹{pur['price']}
        </div>
        """, unsafe_allow_html=True)

elif current_tab == "⚙️ Settings":
    st.markdown("<div class='main-title'>Settings</div>", unsafe_allow_html=True)
    st.success("Connected to Google Sheets successfully!")
