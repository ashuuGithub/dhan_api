# import pdb
# import time
# import datetime
# import traceback
# #import talib
# from Dhan_Tradehull import Tradehull
# import pandas as pd


# client_code = "1105697224"
# token_id = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzM3ODg3NTYwLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNTY5NzIyNCJ9.EHd_1z3dpPCp1o3YaUJIMOKUsle_kWoKn_cplHbsxkZDsdQFY3JMuGPb82HIigviDe8kyiAcvF-Yy6IUzWt9eg"
# tsl = Tradehull(client_code,token_id) # tradehull_support_library



# # data = tsl.get_intraday_data('ACC','NSE',1)
# # print(data)


# # data = tsl.get_intraday_data('banknifty','NSE',10)
# # print(data)


# # available_balance = tsl.get_balance()
# # print("available_balance", available_balance)
# # max_risk_for_the_day = (available_balance*1)/100*-1
# # print("available_balance", available_balance)




# # # ----------------------------------- for banknifty ______________________________
# # ltp1 = tsl.get_ltp_data('BANKNIFTY')
# # print(ltp1)


# # # -----------     for getting the LTP from live market -----------------------------
# # ltp1 = tsl.get_ltp_data('sensex') 
# # print(ltp1)
# # ltp2 = tsl.get_ltp_data('NIFTY')
# # print(ltp2)
# # ltp3 = tsl.get_ltp_data('BANKNIFTY 30 JAN 50000 CALL')
# # print(ltp3)
# # ltp4 = tsl.get_ltp_data('NIFTY 29 AUG 23200 CALL')
# # print(ltp4)


# # # ------------------------ for getting historical data ----------- and save into csv file as well ----------------------
# # BANKNIFY DATA WILL WE FETCH AND DISPLAYED
# # previous_hist_data = tsl.get_historical_data('BANKNIFTY','index','5')  #-- interval value must be ['1','5','15','25','60','DAY']
# # print(previous_hist_data)

# # intraday_hist_data = tsl.get_intraday_data('BANKNIFTY','index',5)
# # # DF = pd.DataFrame(intraday_hist_data)     #--- convert into dataframe and then save into csv file
# # # DF.to_csv('BANKNIFTY.csv')
# # # print(DF.head(10))
# # print(intraday_hist_data)



# # ce_name, pe_name, strike = tsl.ATM_Strike_Selection('NIFTY','05-09-2024')
# # print(ce_name, pe_name, strike)
# # # otm_ce_name, pe_name, ce_OTM_strike, pe_OTM_strike = tsl.OTM_Strike_Selection('NIFTY','05-09-2024',3)
# # # ce_name, pe_name, ce_ITM_strike, pe_ITM_strike = tsl.ITM_Strike_Selection('NIFTY','05-09-2024', 4)



# ce_name, pe_name, strike = tsl.ATM_Strike_Selection('NIFTY','05-09-2024')
# print(ce_name, pe_name, strike)
# # otm_ce_name, pe_name, ce_OTM_strike, pe_OTM_strike = tsl.OTM_Strike_Selection('NIFTY','05-09-2024',3)
# # ce_name, pe_name, ce_ITM_strike, pe_ITM_strike = tsl.ITM_Strike_Selection('NIFTY','05-09-2024', 4)




# # intraday_hist_data = tsl.get_intraday_data(otm_ce_name,'NFO','1')
# # print(intraday_hist_data)
# # intraday_hist_data['rsi'] = talib.RSI(intraday_hist_data['close'], timeperiod=14)


# # lot_size = tsl.get_lot_size('NIFTY 29 AUG 24500 CALL')
# # lot_size = tsl.get_lot_size(otm_ce_name)
# # qty = 2*lot_size

# # # -----------             -----------------how to place order ---------------             ---------------- 

# # orderid1 = tsl.order_placement('NIFTY 29 AUG 24500 CALL','NFO',25, 0.05, 0, 'LIMIT', 'BUY', 'MIS')
# # orderid2 = tsl.order_placement('BANKNIFTY 28 AUG 51600 CALL','NFO',15, 0.05, 0, 'LIMIT', 'BUY', 'MIS')
# # orderid3 = tsl.order_placement('ACC','NSE', 1, 0, 0, 'MARKET', 'BUY', 'MIS')
# # exit_all = tsl.cancel_all_orders()


# # live_pnl = tsl.get_live_pnl()
# # print(live_pnl)
# # if live_pnl < max_risk_for_the_day:
# # 	exit_all = tsl.cancel_all_orders()
# # 	response = tsl.kill_switch('ON')




