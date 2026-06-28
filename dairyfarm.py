import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from datetime import datetime

# పేజీ కాన్ఫిగరేషన్
st.set_page_config(
    page_title="డైరీ ఫామ్ డాష్బోర్డ్",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# గూగుల్ షీట్ పూర్తి URL
sheet_url = "https://docs.google.com/spreadsheets/d/15-g1ftyrveaoJKXziQFlFLTJmqyzhgqFoJG8vuyuknc/edit?usp=drivesdk"

# డేటా లోడింగ్ ఫంక్షన్
@st.cache_resource
def load_data(url):
    try:
        gc = gspread.public()
        workbook = gc.open_by_url(url)
        worksheet = workbook.get_worksheet(0)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"డేటాని రీడ్ చేయడంలో లోపం: {e}")
        return pd.DataFrame()

# డేటాని లోడ్ చేయడం
df = load_data(sheet_url)

# సైడ్బార్లో ఆప్షన్స్
st.sidebar.title("మెనూ")
menu_option = st.sidebar.radio("పేజీని ఎంచుకోండి:", ["హోమ్", "డేటా వ్యూ", "విశ్లేషణ"])

# ప్రధాన శీర్షిక
st.title("🐄 డైరీ ఫామ్ మేనేజ్మెంట్ డాష్బోర్డ్")
st.write("ఇక్కడ మీ రోజువారీ డైరీ డేటా మరియు విశ్లేషణలు ఉంటాయి.")

if df.empty:
    st.info("డేటా లోడ్ అవ్వలేదు లేదా షీట్ ఖాళీగా ఉంది. గూగుల్ షీట్ 'Anyone with the link can view' కింద పబ్లిక్గా షేర్ చేయబడిందని నిర్ధారించుకోండి.")
else:
    if menu_option == "హోమ్":
        st.write("### స్వాగతం!")
        st.write("ఈ డాష్బోర్డ్ ద్వారా మీ డైరీ ఫామ్ డేటాని ఎప్పటికప్పుడు సులభంగా పర్యవేక్షించవచ్చు.")
        
        # ముఖ్యమైన గణాంకాలు
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="మొత్తం రికార్డులు", value=len(df))
        with col2:
            st.metric(label="తొలి తేదీ", value=df['Date'].min() if 'Date' in df.columns else "N/A")
        with col3:
            st.metric(label="చివరి తేదీ", value=df['Date'].max() if 'Date' in df.columns else "N/A")

    elif menu_option == "డేటా వ్యూ":
        st.write("### ముడి డేటా (Raw Data)")
        st.dataframe(df, use_container_width=True)

    elif menu_option == "విశ్లేషణ":
        st.write("### డేటా విజువలైజేషన్")
        
        if 'MilkYield' in df.columns and 'Date' in df.columns:
            try:
                # తేదీని సరియైన ఫార్మాట్కు మార్చడం
                df['Date'] = pd.to_datetime(df['Date'])
                fig = px.line(
                    df, 
                    x='Date', 
                    y='MilkYield', 
                    title='రోజువారీ పాల ఉత్పత్తి',
                    labels={'MilkYield': 'పాల ఉత్పత్తి (లీటర్లు)', 'Date': 'తేదీ'},
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"చార్ట్ రూపొందించడంలో లోపం: {e}")
        else:
            st.warning("చార్ట్ చేయడానికి 'MilkYield' లేదా 'Date' కాలమ్స్ డేటాలో లేవు.")
