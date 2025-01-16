import time
import pandas as pd
from datetime import datetime, timedelta
import logging
import pytz  # For timezone handling
from Dhan_Tradehull import Tradehull

# # Configure logging
# logging.basicConfig(filename="trading_bot.log", level=logging.INFO,
#                     format="%(asctime)s - %(levelname)s - %(message)s")

# Configure logging to log both to a file and the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()  # Prints logs to the console
    ]
)

# Client details
CLIENT_CODE = "1105697224"
TOKEN_ID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzM3ODg3NTYwLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNTY5NzIyNCJ9.EHd_1z3dpPCp1o3YaUJIMOKUsle_kWoKn_cplHbsxkZDsdQFY3JMuGPb82HIigviDe8kyiAcvF-Yy6IUzWt9eg"

# Initialize Tradehull
tsl = Tradehull(CLIENT_CODE, TOKEN_ID)

# Watchlist for historical data
WATCHLIST = ['BANKNIFTY']

# Set timezone (e.g., Indian Standard Time)
IST = pytz.timezone("Asia/Kolkata")

# Calculate the previous trading day
today = datetime.today().date()
if today.weekday() == 0:  # Monday
    previous_date = (datetime.today() - timedelta(days=3)).date()
else:
    previous_date = (datetime.today() - timedelta(days=1)).date()

# Convert previous_date to a timezone-aware datetime at midnight
previous_date = IST.localize(datetime.combine(previous_date, datetime.min.time()))

# Initialize trading variables
trade_executed = False
entry_price = None
stop_loss = None
target_price = None
limit_order_price = None
previous_limit_price = None

while True:
    current_time = datetime.now(IST).time()
    print(current_time)

    # Wait for market to open
    if current_time < datetime.strptime("09:15", "%H:%M").time():
        print("Wait for market to open", current_time)
        time.sleep(10)
        continue

    # Stop trading after market close
    if current_time > datetime.strptime("15:28", "%H:%M").time():
        print("Market is closed", current_time)
        break

    if not trade_executed:
        for stock_name in WATCHLIST:
            try:
                # Fetch today's intraday data
                historical_data = tsl.get_historical_data(stock_name, 'index', '5')
                historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'], errors='coerce').dt.tz_convert(IST)

                # Filter data for the last 2 days
                filtered_data = historical_data[historical_data['timestamp'] >= previous_date].copy()
                filtered_data['EMA_5'] = filtered_data['close'].ewm(span=5, adjust=True).mean()

                # Get the last two completed candles and the running candle
                slc = filtered_data.iloc[-3]  # Second last completed candle
                lcc = filtered_data.iloc[-2]  # Last completed candle
                running_candle = filtered_data.iloc[-1]  # Running candle

                # Check if the last completed candle's low is above its EMA
                if lcc['low'] > lcc['EMA_5']:
                    if limit_order_price is None:
                        # Set the initial limit order
                        limit_order_price = lcc['low']
                        print(f"Initial limit order placed at: {limit_order_price}")
                        logging.info(f"Initial limit order placed at: {limit_order_price}")
                    elif lcc['low'] > previous_limit_price:
                        # Modify the limit order if LCC low is greater
                        limit_order_price = lcc['low']
                        print(f"Limit order modified to: {limit_order_price}")
                        logging.info(f"Limit order modified to: {limit_order_price}")

                    # Update the previous limit order price
                    previous_limit_price = limit_order_price

                # Check if the running candle triggers the limit order
                if limit_order_price is not None:
                    if running_candle['low'] <= limit_order_price <= running_candle['high']:
                        #print(f"Trade executed at: {limit_order_price}")

                        # Entry/stop loss/target price calculation
                        entry_price = limit_order_price
                        stop_loss = round(lcc['high']) + 30
                        stop_loss_distance = stop_loss - entry_price
                        target_price = round(entry_price - (3 * stop_loss_distance))
                        
                        print(f"Trade executed at: {entry_price}")
                        print(f"Entry Price: {entry_price}, Stop Loss: {stop_loss}, Target Price: {target_price}, Entry Time: {datetime.now().time()}")
                        
                        #logging.info(f"Trade executed at: {entry_price}")
                        logging.info(f"Entry Price: {entry_price}, Stop Loss: {stop_loss}, Target Price: {target_price}")


                        # Set the trade executed flag
                        trade_executed = True
                        break  # Exit the watchlist loop

            except Exception as e:
                print(f"Error fetching or processing data for {stock_name}: {e}")
                logging.error(f"Error fetching or processing data for {stock_name}: {e}")


    else:  # After trade execution, monitor stop loss and target price
        try:
            # Fetch the latest intraday data
            historical_data = tsl.get_historical_data('BANKNIFTY', 'index', '5')
            historical_data['EMA_5'] = historical_data['close'].ewm(span=5, adjust=True).mean()
            historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'], errors='coerce').dt.tz_convert(IST)
            filtered_data = historical_data[historical_data['timestamp'] >= previous_date].copy()

            # Check the running candle for stop loss or target hit
            running_candle = filtered_data.iloc[-1]
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if running_candle['high'] >= stop_loss:         #running_candle['low'] <= stop_loss:
                print(f"Stop loss hit at: {stop_loss} [{current_timestamp}]")
                logging.info(f"Stop Loss hit at: {stop_loss} [{current_timestamp}]")
                trade_executed = False
            elif running_candle['low'] >= target_price and running_candle['low'] > running_candle['EMA_5'] + 25: #running_candle['high'] >= target_price:
                print(f"Target price hit at: {target_price} [{current_timestamp}]")
                logging.info(f"Target price hit at: {target_price} [{current_timestamp}]")
                trade_executed = False
            # Check if market close time has been reached (after 15:20)
            elif datetime.now().time() >= pd.to_datetime('15:25:00').time():
                # Exit at the close price of the running candle
                exit_price = running_candle['close']
                print(f"Market closed at: {exit_price}. Exiting trade. [{current_timestamp}]")
                logging.info(f"Market closed at: {exit_price}. Trade exited. [{current_timestamp}]")
                trade_executed = False  # Reset and start scanning again

        except Exception as e:
            print(f"Error monitoring trade for BANKNIFTY: {e}")

    # Sleep for 10 seconds before the next iteration
    time.sleep(20)