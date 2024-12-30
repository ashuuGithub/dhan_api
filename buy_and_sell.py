import time
from dhanhq import dhanhq

client_id = "1105697224"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzM3ODg3NTYwLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNTY5NzIyNCJ9.EHd_1z3dpPCp1o3YaUJIMOKUsle_kWoKn_cplHbsxkZDsdQFY3JMuGPb82HIigviDe8kyiAcvF-Yy6IUzWt9eg"

dhan = dhanhq(client_id,access_token)

#print(dhan)


dhan.place_order(
    #tag='',
    transaction_type=dhan.BUY,
    exchange_segment=dhan.NSE, #bse
    product_type=  dhan.INTRA,   #dhan.INTRA,
    order_type=dhan.MARKET, #limit
    validity='DAY',
    security_id='12913', 
    quantity=10,
    disclosed_quantity=0,
    price=0,
    trigger_price=0,
    after_market_order=False,
    amo_time='OPEN',
    bo_profit_value=0,
    bo_stop_loss_Value=0
   # drv_expiry_date=None,
   # drv_options_type=None,
   # drv_strike_price=None    
)

dhan.get_positions()


# Add a 5-minute buffer
time.sleep(5 * 60)  # Wait for 5 minutes (5 * 60 seconds)

dhan.place_order(
    #tag='',
    transaction_type=dhan.SELL,
    exchange_segment=dhan.NSE, #bse
    product_type=dhan.INTRA,
    order_type=dhan.MARKET, #limit
    validity='DAY',
    security_id='12913',
    quantity=10,
    disclosed_quantity=0,
    price=0,
    trigger_price=0,
    after_market_order=False,
    amo_time='OPEN',
    bo_profit_value=0,
    bo_stop_loss_Value=0  
)