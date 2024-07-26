import os
import pandas as pd
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# データベースの設定
db_filename = 'stock_data.db'
db_path = os.path.join(os.getcwd(), db_filename)
engine = create_engine(f'sqlite:///{db_path}')

def load_stock_data(ticker, days=30):
    query = text("""
        SELECT date, open, high, low, close, adj_close, volume 
        FROM stock_data 
        WHERE ticker=:ticker 
        ORDER BY date DESC 
        LIMIT :days
    """)
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {'ticker': ticker, 'days': days})
            data = result.fetchall()
            if not data:
                logging.error(f"No data found for ticker {ticker}")
                raise ValueError(f"No data found for ticker {ticker}")
            
            df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume'])
            df['date'] = pd.to_datetime(df['date'])  # 日付を日時型に変換
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)  # 昇順に並び替え
            logging.info(f"Loaded data from database for ticker {ticker}")
            return df

    except SQLAlchemyError as e:
        logging.error(f"Database error occurred: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise

def check_ticker_symbol(ticker):
    query = text("SELECT EXISTS(SELECT 1 FROM stock_data WHERE ticker=:ticker)")
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {'ticker': ticker}).scalar()
        return result

    except SQLAlchemyError as e:
        logging.error(f"Database error occurred: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise
