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

# Define file paths for historical data and trades with the updated naming pattern
historical_file_name = f"BankNifty_historical_data_{today}.xlsx"
historical_file_path = os.path.join(os.getcwd(), historical_file_name)

trades_file_name = f"BankNifty_trades_data_{today}.xlsx"
trades_file_path = os.path.join(os.getcwd(), trades_file_name)

# Function to create or open an Excel file
def setup_excel_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)  # Delete existing file
    wb = xw.Book()  # Create new Excel workbook
    wb.save(file_path)
    return wb

# Function to apply 5 EMA strategy logic
def apply_5ema_strategy(data):
    global trades  # Use global to append trades to the list
    # Add 5 EMA column using .loc to avoid the SettingWithCopyWarning
    data.loc[:, 'EMA_5'] = data['close'].ewm(span=5, adjust=True).mean()

    # Apply the 5 EMA strategy
    for i in range(1, len(data) - 1):  # Start from index 1 to allow previous candle comparison
        # Check for short entry condition
        if data['low'].iloc[i] > data['EMA_5'].iloc[i] and data['close'].iloc[i + 1] < data['low'].iloc[i]:
            entry_price = round(data['close'].iloc[i])  # Round the entry price
            entry_time = data['datetime'].iloc[i + 1]

            # Calculate Stop Loss and Target
            stop_loss = round(data['high'].iloc[i])  # Round the stop loss
            stop_loss_distance = stop_loss - entry_price
            target_price = round(entry_price - (3 * stop_loss_distance))  # 3x stop loss distance

            # Simulate exit based on reaching stop loss or target
            exit_price = entry_price
            exit_time = entry_time
            result = "Hold"  # Default result status
            profit_loss = 0  # Initialize profit/loss as 0

            for j in range(i + 2, len(data)):  # Check subsequent candles for exit
                if data['high'].iloc[j] >= stop_loss:  # Stop Loss Hit
                    exit_price = stop_loss
                    exit_time = data['datetime'].iloc[j]
                    result = "Stop Loss Hit"
                    profit_loss = entry_price - exit_price
                    break
                elif data['low'].iloc[j] <= target_price:  # Target Hit
                    exit_price = target_price
                    exit_time = data['datetime'].iloc[j]
                    result = "Target Hit"
                    profit_loss = entry_price - exit_price
                    break

            # Record the trade
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

# Fetch today's historical data and apply the 5 EMA strategy
for stock_name in watchlist:
    try:
        # Fetch today's historical data
        historical_data = tsl.get_historical_data(stock_name, 'index', '1')  # Fetch today's data only

        # Ensure 'timestamp' column exists and convert to datetime
        if 'timestamp' in historical_data.columns:
            historical_data['datetime'] = pd.to_datetime(historical_data['timestamp'], errors='coerce')
        else:
            print(f"No 'timestamp' column found for {stock_name}. Skipping...")
            continue

        # Filter out data for today only
        historical_data['date'] = historical_data['datetime'].dt.date
        historical_data_today = historical_data[historical_data['date'] == today]

        # Apply the 5 EMA strategy to today's data
        apply_5ema_strategy(historical_data_today)

        # Combine the 'date' and 'datetime' columns into a single 'date_time' column
        historical_data_today.loc[:, 'date_time'] = historical_data_today['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Drop the old 'timestamp', 'datetime', and 'date' columns
        historical_data_today = historical_data_today.drop(columns=['timestamp', 'datetime', 'date'])

        # Rearrange the columns so that 'date_time' is the first column
        cols = ['date_time'] + [col for col in historical_data_today.columns if col != 'date_time']
        historical_data_today = historical_data_today[cols]

        # Create and save historical data to its Excel file
        historical_workbook = setup_excel_file(historical_file_path)
        sheet_historical = historical_workbook.sheets.add("Historical Data")
        sheet_historical.range("A1").value = historical_data_today
        print(f"Today's historical data saved to Excel for {stock_name}.")

        # Save historical file before opening
        historical_workbook.save()

        # Open historical Excel file automatically
        historical_workbook.app.visible = True
        historical_workbook.activate()

    except Exception as e:
        print(f"Error fetching or processing historical data for {stock_name}: {e}")

# Save trades to its Excel file
trades_df = pd.DataFrame(trades)
trades_workbook = setup_excel_file(trades_file_path)
sheet_trades = trades_workbook.sheets.add("Trades")
sheet_trades.range("A1").value = trades_df
print("Today's trades saved to Excel.")

# Save and close trades workbook
trades_workbook.save()
trades_workbook.close()
