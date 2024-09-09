from deepmm.utils.db_connection import DataConnection
import os


def down_derivative_midprice_db(db_conn:DataConnection, 
                     start_date:str,
                     end_date:str,
                     start_time:str,
                     end_time:str,
                     time_delay:int=10, 
                     filename:str='data.csv'):
    df = db_conn.get_derivative_midprice_data(start_date=start_date,
                                             end_date=end_date,
                                             start_hour=start_time,
                                             end_hour=end_time,
                                             time_delay=time_delay)
    
    os.makedirs('datasetATDB', exist_ok=True)
    df.to_csv(f"datasetATDB/{filename}", index=False)
    print("Downloaded data from database successfully! from %s to %s" % (start_date, end_date))
    return df

def down_derivative_matched_db(db_conn:DataConnection, 
                     start_date:str,
                     end_date:str,
                     start_time:str,
                     end_time:str,
                     time_delay:int=10, 
                     filename:str='data.csv'):
    df = db_conn.get_derivative_matched_data(start_date=start_date,
                                             end_date=end_date,
                                             start_hour=start_time,
                                             end_hour=end_time,
                                             time_delay=time_delay)
    
    os.makedirs('datasetATDB', exist_ok=True)
    df.to_csv(f"datasetATDB/{filename}", index=False)
    print("Downloaded data from database successfully! from %s to %s" % (start_date, end_date))
    return df