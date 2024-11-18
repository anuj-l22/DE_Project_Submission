import yfinance as yf
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import os
from io import StringIO
import requests
import base64

# MySQL connection setup
def create_connection():
    """
    Establishes a connection to the MySQL database using environment variables.
    Returns:
        mysql.connector.connection: MySQL connection object.
    """
    return mysql.connector.connect(
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        database='project'
    )

# Fetch the latest date in the gold table
def get_latest_date_from_mysql_gold():
    """
    Fetches the latest date in the gold table from MySQL.
    Returns:
        datetime.date: Latest date in the gold table.
    """
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(Date) FROM gold")
    result = cursor.fetchone()
    connection.close()

    return result[0] if result and result[0] else datetime(2020, 1, 1).date()

# Fetch the latest event_id in the events table
def get_latest_event_id_from_mysql_events():
    """
    Fetches the latest event_id in the events table from MySQL.
    Returns:
        int: Latest event_id in the events table.
    """
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(event_id) FROM events")
    result = cursor.fetchone()
    connection.close()

    return result[0] if result and result[0] else 0  # Assuming event_id starts at 1


# Fetch gold price data starting from the last date in the database
def fetch_gold_data(start_date):
    """
    Fetches gold price data from Yahoo Finance starting from the specified date.
    Args:
        start_date (datetime.date): Start date for fetching gold data.
    Returns:
        pd.DataFrame: DataFrame containing the fetched gold data.
    """
    end_date = datetime.now().date()
    gold_data = yf.download('GC=F', start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    if gold_data.empty:
        print("No data fetched from Yahoo Finance.")
        return gold_data

    gold_data.reset_index(inplace=True)
    gold_data['Date'] = gold_data['Date'].dt.date

    # Check if columns are multi-indexed and flatten them
    if isinstance(gold_data.columns, pd.MultiIndex):
        gold_data.columns = ['_'.join(col).strip() for col in gold_data.columns.values]
        print("Flattened multi-indexed columns:", gold_data.columns.tolist())
    else:
        print("Single-level columns:", gold_data.columns.tolist())

    # Define column mapping including 'Date_'
    column_mapping = {
        'Date_': 'Date',  # Rename 'Date_' to 'Date'
        'Adj Close_GC=F': 'Adj Close',
        'Close_GC=F': 'Close',
        'High_GC=F': 'High',
        'Low_GC=F': 'Low',
        'Open_GC=F': 'Open',
        'Volume_GC=F': 'Volume',
        'Adj Close': 'Adj Close',
        'Close': 'Close',
        'High': 'High',
        'Low': 'Low',
        'Open': 'Open',
        'Volume': 'Volume'
    }

    # If columns were flattened, adjust the mapping accordingly
    if isinstance(gold_data.columns, pd.MultiIndex):
        # Extract the field name by splitting
        gold_data = gold_data.rename(columns=lambda x: x.split('_')[0] if '_' in x else x)

    # Rename columns using the updated column_mapping
    gold_data.rename(columns=column_mapping, inplace=True)

    # Verify the columns after renaming
    expected_columns = ['Date', 'Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']
    missing_columns = [col for col in expected_columns if col not in gold_data.columns]
    if missing_columns:
        print(f"Warning: The following expected columns are missing after renaming: {missing_columns}")

    print("Columns after renaming:", gold_data.columns.tolist())
    return gold_data

# Calculate percentage change for gold prices
def calculate_change_percentage(gold_data):
    if 'Close' in gold_data.columns:
        gold_data['Change %'] = gold_data['Close'].pct_change() * 100
        gold_data = gold_data.iloc[1:].reset_index(drop=True)
    else:
        print("Warning: 'Close' column not found in gold data.")
    return gold_data

# Store gold data in MySQL
def store_gold_data_in_mysql(gold_data):
    if gold_data.empty:
        print("No new data to add to the gold table.")
        return

    connection = create_connection()
    cursor = connection.cursor()
    data_to_insert = []
    for idx, row in gold_data.iterrows():
        try:
            date = row['Date']
            close = float(row['Close']) if not pd.isna(row['Close']) else None
            open_price = float(row['Open']) if not pd.isna(row['Open']) else None
            high = float(row['High']) if not pd.isna(row['High']) else None
            low = float(row['Low']) if not pd.isna(row['Low']) else None
            change_pct = float(row['Change %']) if 'Change %' in row and not pd.isna(row['Change %']) else None
            source = 'Yahoo Finance'
            data_to_insert.append((date, close, open_price, high, low, change_pct, source))
        except Exception as e:
            print(f"Error processing row {row}: {e}")

    sql = """
    INSERT INTO gold (Date, Price, Open, High, Low, `Change %`, Source)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        if data_to_insert:
            print("Data to insert:", data_to_insert)
            cursor.executemany(sql, data_to_insert)
            connection.commit()
            print("New gold data loaded into MySQL.")
        else:
            print("No valid data to insert into the gold table.")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        # Optionally, print data that failed to insert for debugging
        for record in data_to_insert:
            print("Failed record:", record)
    finally:
        cursor.close()
        connection.close()

# Fetch the events CSV file from GitHub
def fetch_csv_from_github():
    url = f"https://api.github.com/repos/{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}/contents/{os.getenv('FILE_PATH')}"
    headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # GitHub API returns the file content in base64
        content = response.json().get("content")
        csv_content = StringIO(base64.b64decode(content).decode("utf-8"))
        return pd.read_csv(csv_content)
    else:
        print(f"Failed to fetch the file from GitHub: {response.status_code}")
        return pd.DataFrame()

# Store new data in MySQL
def store_events_data_in_mysql(events_data):
    if events_data.empty:
        print("No new data to add.")
        return

    connection = create_connection()
    cursor = connection.cursor()

    # Prepare data for insertion
    data_to_insert = []
    for _, row in events_data.iterrows():
        data_tuple = (
            row['event_id'],
            row['Name of Incident'],
            row['Date'],
            row['Country'],
            row['Type of Event'],
            row['Outcome']
        )
        data_to_insert.append(data_tuple)

    # Define the SQL statement
    sql = """
    INSERT INTO events (event_id, Name_of_Incident, Date, Country, Type_Of_Event, Outcome)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.executemany(sql, data_to_insert)
        connection.commit()
        print("New events data loaded into MySQL.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# Main ETL process
if __name__ == "__main__":
    # Gold Data ETL
    latest_gold_date = get_latest_date_from_mysql_gold()
    print(f"Latest gold date in DB: {latest_gold_date}")
    start_date = latest_gold_date + timedelta(days=1)
    gold_data = fetch_gold_data(start_date)
    if not gold_data.empty:
        print("Fetched gold data:")
        print(gold_data.head())
        gold_data = calculate_change_percentage(gold_data)
        print("Gold data after calculating change percentage:")
        print(gold_data.head())
        store_gold_data_in_mysql(gold_data)
    else:
        print("No new gold data fetched.")

    # Events Data ETL
    latest_event_id = get_latest_event_id_from_mysql_events()
    print(f"Latest event_id in DB: {latest_event_id}")
    events_data = fetch_csv_from_github()
    if not events_data.empty:
        print("Fetched events data:")
        print(events_data.tail())
        # Ensure event_id is of integer type
        events_data['event_id'] = pd.to_numeric(events_data['event_id'], errors='coerce')
        # Drop rows with NaN event_id
        events_data = events_data.dropna(subset=['event_id'])
        # Convert event_id to integer
        events_data['event_id'] = events_data['event_id'].astype(int)
        # Select new events where event_id > latest_event_id
        new_events_data = events_data[events_data['event_id'] > latest_event_id]
        print(f"New events data to insert: {new_events_data.shape[0]} records")
        store_events_data_in_mysql(new_events_data)
    else:
        print("No new events data fetched.")

