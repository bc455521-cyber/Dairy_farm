import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Dairy Farm Dashboard",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Extracting Google Sheet ID from your URL
sheet_id = "15-g1ftyrveaoJKXziQFlFLTJmqyzhgqFoJG8vuyuknc"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# Data Loading Function (Direct CSV export via public link)
@st.cache_data
def load_data(url):
    try:
        data = pd.read_csv(url)
        return data
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return pd.DataFrame()

# Loading the data
df = load_data(csv_url)

# Sidebar Options
st.sidebar.title("Menu")
menu_option = st.sidebar.radio("Select a page:", ["Home", "Data View", "Analysis"])

# Main Title
st.title("🐄 Dairy Farm Management Dashboard")
st.write("Track and analyze your daily dairy farm operations here.")

if df.empty:
    st.info("Data could not be loaded or the sheet is empty. Please ensure your Google Sheet is shared as 'Anyone with the link can view'.")
else:
    if menu_option == "Home":
        st.write("### Welcome!")
        st.write("This dashboard helps you monitor your dairy farm's key metrics effortlessly.")
        
        # Key Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Records", value=len(df))
        with col2:
            st.metric(label="Earliest Date", value=str(df['Date'].min()) if 'Date' in df.columns else "N/A")
        with col3:
            st.metric(label="Latest Date", value=str(df['Date'].max()) if 'Date' in df.columns else "N/A")

    elif menu_option == "Data View":
        st.write("### Raw Data Table")
        st.dataframe(df, use_container_width=True)

    elif menu_option == "Analysis":
        st.write("### Data Visualization")
        
        if 'MilkYield' in df.columns and 'Date' in df.columns:
            try:
                # Parsing the Date column to proper datetime format
                df['Date'] = pd.to_datetime(df['Date'])
                fig = px.line(
                    df, 
                    x='Date', 
                    y='MilkYield', 
                    title='Daily Milk Production Trend',
                    labels={'MilkYield': 'Milk Production (Liters)', 'Date': 'Date'},
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating chart: {e}")
        else:
            st.warning("Chart cannot be displayed because 'MilkYield' or 'Date' columns are missing in the sheet.")
