import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
API_URL = "https://api.dhan.co/v2/charts/intraday"
CLIENT_ID = os.getenv("CLIENT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
SYMBOL = "BANKNIFTY"
EXCHANGE_SEGMENT = "IDX_I"
INSTRUMENT = "INDEX"
EXPIRY_CODE = 0
SAVE_PATH = r"C:\Users\AshishKumarSen\OneDrive - BITTWOBYTE TECHNOLOGY PRIVATE LIMITED\Bank_Nifty_Treding_File_location"  # Update this path accordingly

# Start and end dates
START_DATE = "2024-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

# Headers for the API request
HEADERS = {
    "Content-Type": "application/json",
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
}

# Create the save path directory if it does not exist
os.makedirs(SAVE_PATH, exist_ok=True)

# Function to fetch data in chunks
def fetch_data_in_chunks(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=5)  # 5-day chunks
    all_data = []  # List to store all chunks of data
    
    while start_date < end_date:
        chunk_end_date = min(start_date + delta, end_date)
        from_date = start_date.strftime("%Y-%m-%d")
        to_date = chunk_end_date.strftime("%Y-%m-%d")
        
        payload = {
            "securityId": "25",
            "exchangeSegment": EXCHANGE_SEGMENT,
            "instrument": INSTRUMENT,
            "interval": "5",
            "fromDate": from_date,
            "toDate": to_date,
        }
        
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'open' in data:
                df = pd.DataFrame(data)
                df['Datetime'] = pd.to_datetime(df['timestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
                all_data.append(df)
            else:
                print(f"Error: 'open' key not found in response for {from_date} to {to_date}.")
        else:
            print(f"Error fetching data: {response.status_code} {response.text}")
        
        start_date += delta
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Fetch data for the entire date range
data_df = fetch_data_in_chunks(START_DATE, END_DATE)

if not data_df.empty:
    data_df.set_index('Datetime', inplace=True)
    data_df['EMA_5'] = data_df['close'].ewm(span=5, adjust=True).mean()
    
    # Save historical data to CSV
    historical_data_file = os.path.join(SAVE_PATH, f'historical_data_{START_DATE}_to_{END_DATE}.csv')
    data_df.to_csv(historical_data_file)
    print(f"Historical data saved to {historical_data_file}.")
    
    # Trading strategy
    trades = []
    market_close_time = pd.to_datetime('15:25:00').time()
    
    for i in range(1, len(data_df) - 1):
        if data_df['low'].iloc[i] > data_df['EMA_5'].iloc[i] and data_df['close'].iloc[i + 1] < data_df['low'].iloc[i]:
            entry_price = round(data_df['close'].iloc[i])
            entry_time = data_df.index[i + 1]
            stop_loss = round(data_df['high'].iloc[i])
            stop_loss_distance = stop_loss - entry_price
            target_price = round(entry_price - (3 * stop_loss_distance))
            
            exit_price, exit_time, result, profit_loss = entry_price, entry_time, "Hold", 0
            for j in range(i + 2, len(data_df)):
                current_time = data_df.index[j].time()
                if current_time >= market_close_time:
                    exit_price = round(data_df['close'].iloc[j])
                    exit_time = data_df.index[j]
                    result = "End of Day"
                    profit_loss = entry_price - exit_price
                    break
                if data_df['high'].iloc[j] >= stop_loss + 30:
                    exit_price = stop_loss
                    exit_time = data_df.index[j]
                    result = "Stop Loss Hit"
                    profit_loss = entry_price - exit_price
                    break
                elif data_df['low'].iloc[j] <= target_price and data_df['low'].iloc[j] > data_df['EMA_5'].iloc[j] + 25:
                    exit_price = max(target_price, data_df['low'].iloc[j])
                    exit_time = data_df.index[j]
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
                'Profit/Loss': profit_loss,
            })
    
    # Save trades to CSV
    trades_df = pd.DataFrame(trades)
    trades_file = os.path.join(SAVE_PATH, f'trades_{START_DATE}_to_{END_DATE}.csv')
    trades_df.to_csv(trades_file, index=False)
    print(f"Trades saved to {trades_file}.")
else:
    print("No data fetched.")
