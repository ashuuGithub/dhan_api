import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
API_URL = "https://api.dhan.co/v2/charts/historical"
CLIENT_ID = os.getenv("CLIENT_ID")  # Fetch CLIENT_ID from .env
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Fetch ACCESS_TOKEN from .env
SYMBOL = "LODHA"  # Desired symbol, e.g., "LODHA"
EXCHANGE_SEGMENT = "NSE_EQ"  # Exchange segment
INSTRUMENT = "EQUITY"  # Instrument type
EXPIRY_CODE = 0  # Typically 0 for equity instruments
SAVE_PATH = r"C:\Users\AshishKumarSen\OneDrive - BITTWOBYTE TECHNOLOGY PRIVATE LIMITED\Bank_Nifty_Treding_File_location"

# Custom Date Range: August 2024 to December 2024
START_DATE = "2015-01-01"  # Start date for fetching data
END_DATE = "2024-12-31"  # End date for fetching data

# Headers for the request
HEADERS = {
    "Content-Type": "application/json",
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID
}

# Payload for the request
payload = {
    "securityId": "1333",  # Replace with the actual security ID for "LODHA"
    "exchangeSegment": EXCHANGE_SEGMENT,
    "instrument": INSTRUMENT,
    "expiryCode": EXPIRY_CODE,
    "fromDate": START_DATE,
    "toDate": END_DATE
}

# Create the save path directory if it does not exist
os.makedirs(SAVE_PATH, exist_ok=True)

# Fetch historical data from the Dhan API
response = requests.post(API_URL, headers=HEADERS, json=payload)

if response.status_code == 200:
    data = response.json()
    
    # Validate API response
    if 'open' in data:
        # Convert API response to pandas DataFrame
        df = pd.DataFrame(data)
        df['Datetime'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        df.set_index('Datetime', inplace=True)
        
        # Calculate the 5 EMA
        df['EMA_5'] = df['close'].ewm(span=5, adjust=True).mean()

        # Save historical data to CSV
        historical_data_file = os.path.join(SAVE_PATH, f'historical_data_lodha_{START_DATE}_to_{END_DATE}.csv')
        df.to_csv(historical_data_file)
        print(f"Historical data saved to {historical_data_file}.")

        # Initialize an empty list to store trade results
        trades = []

        # Set market close time (3:30 PM IST)
        market_close_time = pd.to_datetime('15:25:00').time()

        # Apply the trading strategy
        for i in range(1, len(df) - 1):
            if df['low'].iloc[i] > df['EMA_5'].iloc[i] and df['close'].iloc[i + 1] < df['low'].iloc[i]:
                entry_price = round(df['close'].iloc[i])
                entry_time = df.index[i + 1]

                # Stop Loss and Target Calculation
                stop_loss = round(df['high'].iloc[i])
                stop_loss_distance = stop_loss - entry_price
                target_price = round(entry_price - (3 * stop_loss_distance))

                # Simulate exit based on stop loss, target, or market close
                exit_price, exit_time, result, profit_loss = entry_price, entry_time, "Hold", 0
                for j in range(i + 2, len(df)):
                    current_time = df.index[j].time()
                    if current_time >= market_close_time:
                        exit_price = round(df['close'].iloc[j])
                        exit_time = df.index[j]
                        result = "End of Day"
                        profit_loss = entry_price - exit_price
                        break
                    if df['high'].iloc[j] >= stop_loss + 30:
                        exit_price = stop_loss
                        exit_time = df.index[j]
                        result = "Stop Loss Hit"
                        profit_loss = entry_price - exit_price
                        break
                    elif df['low'].iloc[j] <= target_price and df['low'].iloc[j] > df['EMA_5'].iloc[j] + 25:
                        exit_price = max(target_price, df['low'].iloc[j])
                        exit_time = df.index[j]
                        result = "Target Hit"
                        profit_loss = entry_price - exit_price
                        break
                
                trades.append({
                    'Entry Time': entry_time,
                    'Entry Price': entry_price,
                    'Stop Loss': stop_loss,
                    'Target Price': target_price,
                    'Exit Time': exit_time,
                    'Exit Price': exit_price,
                    'Result': result,
                    'Profit/Loss': profit_loss
                })

        # Save trades to CSV
        trades_df = pd.DataFrame(trades)
        trades_file = os.path.join(SAVE_PATH, f'lodha_trades_{START_DATE}_to_{END_DATE}.csv')
        trades_df.to_csv(trades_file, index=False)
        print(f"Trades saved to {trades_file}.")
    else:
        print("Error: 'open' key not found in response.")
else:
    print("Error fetching data from Dhan API:", response.status_code, response.text)
