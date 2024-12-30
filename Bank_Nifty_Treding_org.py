import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Set up the parameters
symbol = "LODHA.NS" #"^NSEBANK"  # Bank Nifty symbol on Yahoo Finance
# symbol = "^NSEI"  # Bank Nifty symbol on Yahoo Finance
# symbol = "BTC-USD"  # Bank Nifty symbol on Yahoo Finance
interval = "5m"      # 5-minute interval
#start_date = "2024-11-01"       # Download data for the past 5 days, adjust as needed
start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')

# Download the data
df = yf.download(tickers=symbol, interval=interval, start=start_date)
df.reset_index(inplace=True)
df['Datetime'] = df['Datetime'].dt.tz_convert('Asia/Kolkata')  # Convert to IST
# df.set_index('Datetime', inplace=True)
# Calculate the 5 EMA
df['EMA_5'] = df['Close'].ewm(span=5, adjust=True).mean()

# Initialize an empty list to store trade results
trades = []

# Set the market close time (3:30 PM for Indian stock market)
market_close_time = pd.to_datetime('15:25:00').time()

# Loop through each row to apply the strategy
for i in range(1, len(df) - 1):  # Start from index 1 to allow previous candle comparison
    # Check for short entry condition
    if df['Low'].iloc[i].item() > df['EMA_5'].iloc[i] and df['Close'].iloc[i + 1].item() < df['Low'].iloc[i].item():
        entry_price = round(df['Close'].iloc[i].item())  # Round the entry price
        entry_time = df['Datetime'].iloc[i + 1]
        
        # Calculate Stop Loss and Target
        stop_loss = round(df['High'].iloc[i].item())  # Round the stop loss
        stop_loss_distance = stop_loss - entry_price  # Difference between entry price and stop loss
        target_price = round(entry_price - (3 * stop_loss_distance))  # Round the target price at 3x stop loss distance
        
        # Simulate exit based on reaching stop loss or target, or end of day
        exit_price = entry_price
        exit_time = entry_time
        result = "Hold"  # Default result status
        profit_loss = 0  # Initialize profit/loss as 0

        for j in range(i + 2, len(df)):  # Check subsequent candles for exit
            # Check if current time is after market close (3:30 PM)
            current_time = df['Datetime'].iloc[j].time()
            if current_time >= market_close_time:  # End of the day reached
                exit_price = round(df['Close'].iloc[j].item())  # Close at the last price of the day
                exit_time = df['Datetime'].iloc[j]
                result = "End of Day"
                profit_loss = entry_price - exit_price  # Profit or loss based on close price
                break
            if df['High'].iloc[j].item() >= stop_loss + 30:  # Stop loss hit
                exit_price = stop_loss
                exit_time = df['Datetime'].iloc[j]
                result = "Stop Loss Hit"
                profit_loss = entry_price - exit_price  # Loss (will be negative for stop loss)
                break
            elif df['Low'].iloc[j].item() <= target_price and df['Low'].iloc[j].item() > df['EMA_5'].iloc[j] + 25:  # Target hit
                exit_price = max( target_price, df['Low'].iloc[j].item() )
                exit_time = df['Datetime'].iloc[j]
                result = "Target Hit"
                profit_loss = entry_price - exit_price  # Profit (will be positive for target hit)
                break
        
        # Record the trade with result and profit/loss
        trades.append({
            'Entry Time': entry_time,
            'Entry Price': entry_price,
            'Stop Loss': stop_loss,
            'Target Price': target_price,
            'Exit Time': exit_time,
            'Exit Price': exit_price,
            'Result': result,  # Indicates whether target, stop loss, or end of day was hit
            'Profit/Loss': profit_loss  # Records the profit or loss for each trade
        })

# Convert trade data to DataFrame and save to Excel
trades_df = pd.DataFrame(trades)

# Save to Excel
trades_df.to_csv(r'C:\Users\AshishKumarSen\OneDrive - BITTWOBYTE TECHNOLOGY PRIVATE LIMITED\Bank_Nifty_Treding_File_location\banknifty_trades_short.csv', index=False)

print("Trades have been saved to banknifty_trades.xlsx")
