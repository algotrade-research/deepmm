from pathlib import Path

from utils.date_management import get_num_days_to_maturity

from utils.db_connection import DataConnection

from utils.loading_file import load_yaml
from utils.download import down_derivative_midprice_db, down_derivative_matched_db
import pandas as pd

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

def split_data_by_month(df, ratio):
    """
    Split data by month
    """
    unique_symbol = df['tickersymbol'].unique()


    train_symbol = unique_symbol[:int(len(unique_symbol) * (1-ratio))]
    val_symbol = unique_symbol[int(len(unique_symbol) * (1-ratio)):]

    train_df = df[df['tickersymbol'].isin(train_symbol)]
    val_df = df[df['tickersymbol'].isin(val_symbol)]

    return train_df, val_df


def main():
    
    db_account = load_yaml(ROOT / "configs" / "usr" / "db_account.yaml")
    # Data query
    user, password, host, port, db_name =   db_account['user'],\
                                            db_account['pass'], \
                                            db_account['host'], \
                                            db_account['port'], \
                                            db_account['database']
    db_conn = DataConnection(user, password, host, port, db_name)
    start = '2023-01-01'    
    end = '2023-12-31'
    sql_query = f"""
        SELECT m.datetime as datetime, m.price as price, m.tickersymbol as tickersymbol
        FROM quote.futurecontractcode f
        JOIN quote.matched m
        ON f.tickersymbol = m.tickersymbol
        AND DATE(m.datetime) = f.datetime
        WHERE m.datetime BETWEEN '{start}' AND '{end}'
        AND f.futurecode = 'VN30F1M'
        ORDER BY DATE(f.datetime), f.datetime, m.datetime;"""
    
    
    df = db_conn.query_to_df(sql_query)
    
    train_df, val_df = split_data_by_month(df, 0.2)

    train_df.to_csv('datasetATDB/train.csv', index=False)
    val_df.to_csv('datasetATDB/val.csv', index=False)



    # start = '2024-01-01'
    # end = '2024-12-01'
    # sql_query = f"""
    #     SELECT m.datetime as datetime, m.price as price, m.tickersymbol as tickersymbol
    #     FROM quote.futurecontractcode f
    #     JOIN quote.matched m
    #     ON f.tickersymbol = m.tickersymbol
    #     AND DATE(m.datetime) = f.datetime
    #     WHERE m.datetime BETWEEN '{start}' AND '{end}'
    #     AND f.futurecode = 'VN30F1M'
    #     ORDER BY DATE(f.datetime), f.datetime, m.datetime;"""

    # df = db_conn.query_to_df(sql_query)
    # df.to_csv('datasetATDB/test.csv', index=False)

    # down_derivative_matched_db(db_conn, 
    #                            '2023-01-01', 
    #                            '2023-07-31', 
    #                            '08:30:00', 
    #                            '15:00:45', 
    #                            1, 
    #                            'train_6m.csv')

    # down_derivative_matched_db(db_conn, 
    #                            '2023-09-15', 
    #                            '2023-12-15', 
    #                            '08:30:00', 
    #                            '15:00:45',  
    #                            1, 
    #                            'val.csv')


if __name__ == "__main__":
    main()
