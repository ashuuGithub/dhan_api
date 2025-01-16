# with header columns name as 'Entry Time', 'Entry Price', 'Stop Loss', 'Target Price', 'Exit Time', 'Exit Price', 'Result', 'Profit/Loss'
# Import necessary libraries
from Dhan_Tradehull import Tradehull
import pandas as pd
from datetime import datetime
import os
import xlwings as xw  # For Excel file management

# Client details
client_code = "1105697224"
token_id = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzM3ODg3NTYwLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNTY5NzIyNCJ9.EHd_1z3dpPCp1o3YaUJIMOKUsle_kWoKn_cplHbsxkZDsdQFY3JMuGPb82HIigviDe8kyiAcvF-Yy6IUzWt9eg"
tsl = Tradehull(client_code, token_id)  # Initialize Tradehull

# Watchlist for historical data
watchlist = ['BANKNIFTY']

# Initialize an empty list to store trades
trades = []

# Get today's date
today = datetime.today().date()

# Define file paths for historical data and trades
historical_file_name = f"BankNifty_historical_data_{today}.xlsx"
historical_file_path = os.path.join(os.getcwd(), historical_file_name)

trades_file_name = f"BankNifty_trades_data_{today}.xlsx"
trades_file_path = os.path.join(os.getcwd(), trades_file_name)

# Initialize variables to track the last timestamp
last_historical_timestamp = None
last_trade_timestamp = None

# Function to create or open an Excel file
def setup_excel_file(file_path, sheet_name):
    if os.path.exists(file_path):
        wb = xw.Book(file_path)  # Open existing workbook
        if sheet_name not in [sheet.name for sheet in wb.sheets]:
            wb.sheets.add(sheet_name)  # Add sheet if not present
    else:
        wb = xw.Book()  # Create new Excel workbook
        wb.save(file_path)
        wb.sheets.add(sheet_name)  # Add the required sheet
    return wb

# Function to append only new data to Excel
def append_new_data_to_excel(file_path, sheet_name, data, last_timestamp_col, last_timestamp):
    if data.empty:
        return last_timestamp  # No data to append

    # Filter data for new rows based on the last timestamp
    if last_timestamp:
        new_data = data[data[last_timestamp_col] > last_timestamp]
    else:
        new_data = data

    if not new_data.empty:
        wb = setup_excel_file(file_path, sheet_name)
        sheet = wb.sheets[sheet_name]
        
        # Read existing data to check if the sheet has data
        existing_data = sheet.range("A1").expand().value  # Read existing data if any
        
        # Write headers if the sheet is empty
        if not existing_data or (isinstance(existing_data, list) and len(existing_data) <= 1):
            sheet.range("A1").value = new_data.columns.tolist()  # Write headers
            start_row = 2  # Data starts after the headers
        else:
            start_row = len(existing_data) + 1  # Append after existing data

        # Append new rows
        sheet.range(f"A{start_row}").value = new_data.values.tolist()
        wb.save()

        # Update the last timestamp
        last_timestamp = new_data[last_timestamp_col].max()

    return last_timestamp

# Function to apply 5 EMA strategy logic
def apply_5ema_strategy(data):
    global trades
    data.loc[:, 'EMA_5'] = data['close'].ewm(span=5, adjust=True).mean()

    for i in range(1, len(data) - 1):
        if data['low'].iloc[i] > data['EMA_5'].iloc[i] and data['close'].iloc[i + 1] < data['low'].iloc[i]:
            entry_price = round(data['close'].iloc[i])
            entry_time = data['datetime'].iloc[i + 1]
            stop_loss = round(data['high'].iloc[i])
            stop_loss_distance = stop_loss - entry_price
            target_price = round(entry_price - (3 * stop_loss_distance))

            exit_price = entry_price
            exit_time = entry_time
            result = "Hold"
            profit_loss = 0

            for j in range(i + 2, len(data)):
                if data['high'].iloc[j] >= stop_loss:
                    exit_price = stop_loss
                    exit_time = data['datetime'].iloc[j]
                    result = "Stop Loss Hit"
                    profit_loss = entry_price - exit_price
                    break
                elif data['low'].iloc[j] <= target_price:
                    exit_price = target_price
                    exit_time = data['datetime'].iloc[j]
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

# Main loop to process data and append
while True:
    for stock_name in watchlist:
        try:
            # Fetch today's intraday data
            historical_data = tsl.get_intraday_data(stock_name, 'index', 5)

            if 'timestamp' in historical_data.columns:
                historical_data['datetime'] = pd.to_datetime(historical_data['timestamp'], errors='coerce')
            else:
                print(f"No 'timestamp' column found for {stock_name}. Skipping...")
                continue

            historical_data['date'] = historical_data['datetime'].dt.date
            historical_data_today = historical_data[historical_data['date'] == today]

            # Apply 5 EMA strategy
            apply_5ema_strategy(historical_data_today)

            # Prepare historical data
            historical_data_today.loc[:, 'date_time'] = historical_data_today['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            historical_data_today = historical_data_today.drop(columns=['timestamp', 'datetime', 'date'])
            cols = ['date_time'] + [col for col in historical_data_today.columns if col != 'date_time']
            historical_data_today = historical_data_today[cols]

            # Append new historical data to its Excel file
            last_historical_timestamp = append_new_data_to_excel(
                historical_file_path, "Historical Data", historical_data_today, "date_time", last_historical_timestamp
            )
            print(f"Appended new historical data for {stock_name}.")

        except Exception as e:
            print(f"Error fetching or processing historical data for {stock_name}: {e}")

    # Append new trades to its Excel file
    trades_df = pd.DataFrame(trades)

    # Ensure trades DataFrame has headers even if empty
    if trades_df.empty:
        trades_df = pd.DataFrame(columns=[
            'Entry Time', 'Entry Price', 'Stop Loss', 'Target Price',
            'Exit Time', 'Exit Price', 'Result', 'Profit/Loss'
        ])

    last_trade_timestamp = append_new_data_to_excel(
        trades_file_path, "Trades", trades_df, "Entry Time", last_trade_timestamp
    )
    print("Appended new trades to Excel.")
