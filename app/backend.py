import numpy as np
import pandas as pd
import mysql.connector
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# MySQL connection setup
def create_connection():
    return mysql.connector.connect(
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        database='project'
    )

# Fetch data from the gold table
def fetch_gold_data_from_mysql():
    connection = create_connection()
    query = "SELECT * FROM gold"
    gold_df = pd.read_sql(query, connection)
    connection.close()
    return gold_df

# Fetch data from the events table
def fetch_events_data_from_mysql():
    connection = create_connection()
    query = "SELECT * FROM events"
    events_df = pd.read_sql(query, connection)
    connection.close()
    return events_df

# Function to determine top 15 event types and encode
def encode_top_15_event_types(events_df):
    event_counts = events_df['Type_of_Event'].value_counts()
    top_15_events = event_counts.nlargest(15).index.tolist()

    def event_encoder(event_type):
        if pd.isna(event_type):
            return -1  # Set -1 for no event (NaN values)
        elif event_type in top_15_events:
            return top_15_events.index(event_type)
        else:
            return 15  # Encode all other event types as 15

    events_df['Encoded_Event_Type'] = events_df['Type_of_Event'].apply(event_encoder)
    return events_df

# Function to perform feature engineering and combine data
def prepare_features(gold_df, events_df):
    gold_df['Date'] = pd.to_datetime(gold_df['Date'])
    events_df['Date'] = pd.to_datetime(events_df['Date'])
    
    events_df = encode_top_15_event_types(events_df)
    data = pd.merge(gold_df, events_df, on='Date', how='left')
    
    data['Event_Occurred'] = data['event_id'].notnull().astype(int)
    data['Encoded_Event_Type'] = data['Encoded_Event_Type'].fillna(-1).astype(int)
    data.loc[data['Event_Occurred'] == 0, 'Encoded_Event_Type'] = -1

    le_outcome = LabelEncoder()
    data['Encoded_Outcome'] = le_outcome.fit_transform(data['Outcome'].fillna("No Event"))
    data.loc[data['Event_Occurred'] == 0, 'Encoded_Outcome'] = -1

    data['Price_Lag1'] = data['Price'].shift(1)
    data['Price_Lag2'] = data['Price'].shift(2)

    if 'Change %' in data.columns:
        data['7d_avg_price'] = data['Price'].rolling(window=7).mean()
        data['7d_avg_change'] = data['Change %'].rolling(window=7).mean()
    else:
        data['Change %'] = data['Price'].pct_change() * 100
        data['7d_avg_price'] = data['Price'].rolling(window=7).mean()
        data['7d_avg_change'] = data['Change %'].rolling(window=7).mean()

    data.fillna(0, inplace=True)
    
    columns_to_drop = ['event_id', 'Type_of_Event', 'Outcome', 'Name_of_Incident', 'Country', 'Source']
    for col in columns_to_drop:
        if col in data.columns:
            data.drop(columns=[col], inplace=True)
    
    return data

# Full workflow function for training and prediction
def generate_prediction(future_event_date, future_event_type, num_days):
    # Step 1: Fetch data from MySQL
    gold_df = fetch_gold_data_from_mysql()
    events_df = fetch_events_data_from_mysql()
    
    # Step 2: Prepare features
    training_data = prepare_features(gold_df, events_df)

    # Step 3: Train model
    data = training_data.copy()
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)
    
    event_columns = ['Encoded_Event_Type']
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_events = encoder.fit_transform(data[event_columns])
    encoded_event_df = pd.DataFrame(
        encoded_events,
        index=data.index,
        columns=encoder.get_feature_names_out(event_columns)
    )
    data = pd.concat([data[['Price', "Price_Lag1"]], encoded_event_df], axis=1)

    train_data, test_data = train_test_split(data, test_size=0.02, shuffle=False)
    X_train = train_data.drop(columns='Price')
    y_train = train_data['Price']
    X_test = test_data.drop(columns='Price')
    y_test = test_data['Price']

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    predictions = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"Linear Regression RMSE: {rmse:.2f}")

    # Step 4: Predict future prices
    last_test_date = test_data.index[-1]
    start_date = last_test_date + pd.Timedelta(days=1)
    end_date = pd.to_datetime(future_event_date) + pd.Timedelta(days=num_days)
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')

    last_known_price = test_data['Price'].iloc[-1]
    prev_price = last_known_price
    future_prices = []

    for date in all_dates:
        features = {col: 0 for col in X_train.columns}
        if date == pd.to_datetime(future_event_date):
            event_type_value = [[future_event_type]]
        else:
            event_type_value = [[-1]]

        encoded_event = encoder.transform(event_type_value)
        for idx, col in enumerate(encoder.get_feature_names_out(event_columns)):
            features[col] = encoded_event[0][idx]

        features['Price_Lag1'] = prev_price
        features_df = pd.DataFrame([features], index=[date])
        features_df = features_df[X_train.columns]
        
        features_scaled = scaler.transform(features_df)
        predicted_price = model.predict(features_scaled)[0]
        future_prices.append(predicted_price)
        prev_price = predicted_price

    forecast_df = pd.DataFrame({'Date': all_dates, 'Forecasted Price': future_prices})
    forecast_df.set_index('Date', inplace=True)

    plt.figure(figsize=(14, 8))
    plt.plot(test_data.index[-100:], test_data['Price'][-100:], label='Historical Price', color='black')
    plt.plot(forecast_df.index, forecast_df['Forecasted Price'], label='Forecasted Price', color='blue')
    plt.xlabel('Date')
    plt.ylabel('Gold Price')
    plt.title('Gold Price Forecast')
    plt.legend()
    plt.show()

    return forecast_df
