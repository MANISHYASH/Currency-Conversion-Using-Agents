import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load API Key from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")  # Fetch from .env file

# API Endpoints
BASE_URL = "https://api.apilayer.com/exchangerates_data/latest"
HISTORICAL_URL = "https://api.apilayer.com/exchangerates_data/timeseries"

# Streamlit Page Configuration
st.set_page_config(page_title="💱 Currency Converter", page_icon="💰", layout="wide")

# Title
st.title("💱 Currency Converter")

# Fetch available currencies
@st.cache_data
def get_currencies():
    url = f"{BASE_URL}?apikey={API_KEY}"
    response = requests.get(url).json()
    if "rates" in response:
        return sorted(response["rates"].keys())
    return ["USD", "INR", "EUR", "GBP", "CAD"]  # Default if API fails

currencies = get_currencies()

# Input Section
col1, col2 = st.columns(2)
with col1:
    amount = st.number_input("Enter Amount:", min_value=0.01, step=0.01)
with col2:
    from_currency = st.selectbox("From Currency", currencies, index=currencies.index("USD"))
    to_currency = st.selectbox("To Currency", currencies, index=currencies.index("INR"))

# Function to Convert Currency
def convert_currency(amount, from_currency, to_currency):
    url = f"{BASE_URL}?base={from_currency}&apikey={API_KEY}"
    response = requests.get(url).json()
    if "rates" in response and to_currency in response["rates"]:
        exchange_rate = response["rates"][to_currency]
        converted_amount = amount * exchange_rate
        return converted_amount, exchange_rate
    else:
        return None, None

# Fetch Historical Data
def get_historical_data(from_currency, to_currency):
    end_date = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    url = f"{HISTORICAL_URL}?apikey={API_KEY}&start_date={start_date}&end_date={end_date}&base={from_currency}&symbols={to_currency}"
    response = requests.get(url).json()

    if "rates" in response:
        dates = sorted(response["rates"].keys())  # Sort dates
        rates = [response["rates"][date][to_currency] for date in dates]
        return dates, rates
    return [], []

# Convert Button
if st.button("Convert Now"):
    if from_currency == to_currency:
        st.warning("⚠️ Please select different currencies!")
    else:
        converted_amount, exchange_rate = convert_currency(amount, from_currency, to_currency)
        if converted_amount:
            # Black Font Output
            st.write(f"### 💵 {amount} {from_currency} = **{converted_amount:.2f} {to_currency}**")
            st.write(f"#### 📈 Exchange Rate: **{exchange_rate:.4f}**")

            # Display Graph
            dates, rates = get_historical_data(from_currency, to_currency)
            if dates:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=rates, mode="lines+markers", name=f"{from_currency} to {to_currency}"))
                fig.update_layout(title=f"{from_currency} to {to_currency} Exchange Rate (Last 30 Days)", xaxis_title="Date", yaxis_title="Exchange Rate")
                st.plotly_chart(fig)
        else:
            st.error("❌ Error: Unable to fetch exchange rates.")
