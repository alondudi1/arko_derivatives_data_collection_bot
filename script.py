import yfinance as yf
import pandas as pd
from datetime import datetime
import os

ticker_symbol = "ARKO"
ticker = yf.Ticker(ticker_symbol)
today_str = datetime.now().strftime('%Y-%m-%d')
file_name = "ARKO_OI_Tracker.csv"

all_data = []
for exp in ticker.options:
    try:
        chain = ticker.option_chain(exp)
        calls, puts = chain.calls.copy(), chain.puts.copy()
        calls['Type'], puts['Type'] = 'Call', 'Put'
        for df in [calls, puts]:
            df['Expiration'] = exp
            all_data.append(df[['strike', 'Expiration', 'Type', 'openInterest']])
    except:
        continue

current_snapshot = pd.concat(all_data).rename(columns={'openInterest': today_str})

if os.path.exists(file_name):
    master_df = pd.read_csv(file_name)
    master_df = pd.merge(master_df, current_snapshot, on=['strike', 'Expiration', 'Type'], how='outer')
else:
    master_df = current_snapshot

master_df.to_csv(file_name, index=False)
