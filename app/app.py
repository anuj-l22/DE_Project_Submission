import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from backend import generate_prediction  # Import the updated backend function

# Set up page configuration
st.set_page_config(page_title="Gold Price Prediction Dashboard", page_icon="💰", layout="centered")

# Title and Introduction
st.title("📈 Gold Price Prediction in Sync with World Events")
st.markdown("""
    Welcome to the **Gold Price Prediction Dashboard**! This tool leverages machine learning to forecast gold prices by 
    considering the impact of various global events, such as economic policies, natural disasters, and geopolitical crises. 
    By analyzing patterns in historical data, the model generates insights to help predict future price trends.
""")

with st.expander("📊 About the Dataset"):
    st.markdown("""
    This project uses a combination of historical gold prices and event data collected over years. Key features include:
    
    - **Date**: Daily gold prices covering a substantial historical period.
    - **Price Information**: Open, high, low, close prices of gold each day.
    - **Event Data**: Significant world events categorized by types (Economic Policy Change, War, Natural Disaster, etc.).
    - **Event Encoding**: Events are encoded based on their type and impact, helping the model understand patterns.
    
    The dataset is structured to capture how global events influence gold prices, providing the foundation for accurate forecasting.
    """)

# Display images side by side
col1, col2 = st.columns(2)

with col1:
    st.image("Gold_Price_Trend.png", caption="Global Gold Market Trends over the Years")

with col2:
    st.image("Types_of_Events.png", caption="Top 10 Event Types Influencing Gold Prices")

# Event Type Encoding dictionary including "No Event"
event_type_encoding = {
    "No Event": -1,
    "Political": 0,
    "Disaster": 1,
    "Terrorism": 2,
    "Military Action": 3,
    "Diplomatic/International": 4,
    "Economic": 5,
    "Legislative/Judicial": 6,
    "Legislation": 7,
    "Aviation": 8,
    "Peace Process": 9,
    "Sports": 10,
    "Scientific/Exploration": 11,
    "International Sports Event": 12,
    "Independence": 13,
    "Revolution": 14,
    "Other": 15
}

# User Input Section
st.subheader("🗓️ Make a Prediction")
st.markdown("""
    Select a future event date, describe the event's impact, and specify the number of days you wish to forecast.
    Choose one of the pre-defined categories, including **'No Event'** if you want to model a scenario with no event.
""")

# Dropdown for Event Types
future_event_date = st.date_input("Select a future event date")
selected_event_type = st.selectbox("Event Type", options=list(event_type_encoding.keys()))
num_days = st.number_input("Number of days to predict", min_value=1, max_value=365, value=7, step=1)

# Convert selected event type to encoding
future_event_type = event_type_encoding[selected_event_type]

# Prediction Button and Display
if st.button("🔍 Predict Gold Prices"):
    st.write("Generating forecast... please wait.")
    
    # Call the backend function and fetch forecasted data and plot
    forecast_df = generate_prediction(future_event_date, future_event_type, num_days)
    
    st.write("### Forecasted Prices")
    st.write(forecast_df)
    
    # Render the plot
    st.write("### Forecasted Price Trend")
    plt.figure(figsize=(14, 8))
    plt.plot(forecast_df.index, forecast_df['Forecasted Price'], label='Forecasted Price', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Gold Price')
    plt.title('Gold Price Forecast')
    plt.legend()
    st.pyplot(plt)  # Display the plot using Streamlit
    
    st.markdown("**Predicted Gold Prices over Time**")

# Section on Prediction Methodology within a tab
st.subheader("Prediction Methodology")
tab1, tab2 = st.tabs(["🔍 How Predictions Work", "📈 Prediction Steps"])

with tab1:
    st.markdown("""
        Our machine learning model employs time series analysis techniques, using historical gold prices and event-related data to 
        make accurate predictions. The model has been trained to recognize how different types of events impact price trends, 
        allowing it to adapt and improve with each prediction.
    """)

with tab2:
    st.markdown("""
    **Prediction Steps**:
    1. **Historical Data Analysis**: Patterns in past data are identified, especially during event-driven fluctuations.
    2. **Event Encoding**: Events are categorized and encoded, giving the model a structure to assess likely impacts.
    3. **Trend Forecasting**: Using these insights, the model forecasts future price trends based on the specified event and forecast duration.
    """)

# Additional Resources Section with structured links
st.subheader("📚 Additional Resources")
st.markdown("""
**Gold Market Resources**
- [World Gold Council - Market Insights](https://www.gold.org)
- [Current Trends in Global Markets](https://www.investopedia.com/markets/)
- [Gold Price News and Analysis](https://www.investing.com)

**Global Event Resources**
- [Council on Foreign Relations - Global Events](https://www.cfr.org)
""")

# Footer and Credits
st.markdown("""
---
*Project by: Anuj Rajan Lalla*  
*Powered by: Streamlit, Python, MySQL*
""")
