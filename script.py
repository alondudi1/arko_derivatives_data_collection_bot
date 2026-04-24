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
            
            # המרת תאריך העסקה האחרונה לפורמט תאריך נקי (ללא שעות ואזורי זמן)
            df['lastTradeDate'] = pd.to_datetime(df['lastTradeDate']).dt.tz_localize(None).dt.date
            current_date = datetime.now().date()
            
            # אם העסקה האחרונה לא קרתה היום, ה-Volume האמיתי להיום הוא 0
            df.loc[df['lastTradeDate'] < current_date, 'volume'] = 0
            
            all_data.append(df[['strike', 'Expiration', 'Type', 'openInterest', 'volume']])
    except:
        continue

# יצירת צילום מצב עדכני עם שמות עמודות הכוללים את סוג הנתון והתאריך
current_snapshot = pd.concat(all_data)
current_snapshot = current_snapshot.rename(columns={
    'openInterest': f'OI_{today_str}',
    'volume': f'Vol_{today_str}'
})

if os.path.exists(file_name):
    master_df = pd.read_csv(file_name)
    
    # בדיקה ומחיקה של עמודות התאריך הנוכחי כדי למנוע כפילויות של _x ו-_y
    cols_to_check = [f'OI_{today_str}', f'Vol_{today_str}']
    existing_cols = [col for col in cols_to_check if col in master_df.columns]
    if existing_cols:
        master_df = master_df.drop(columns=existing_cols)

    # מיזוג לפי המפתחות הקבועים
    master_df = pd.merge(master_df, current_snapshot, on=['strike', 'Expiration', 'Type'], how='outer')
else:
    master_df = current_snapshot

master_df = master_df.fillna(0)

master_df.to_csv(file_name, index=False)
