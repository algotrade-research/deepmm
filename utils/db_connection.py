import psycopg2
import pandas as pd
import time

from datetime import date, timedelta, datetime

class DataConnection():
    def __init__(self, username, password, host, port, db_name):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.connection = psycopg2.connect(
            dbname=self.db_name,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port
        )
        self.cursor = self.connection.cursor()

    def query_to_df(self, query):
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        columns = [desc[0] for desc in self.cursor.description]
        df = pd.DataFrame(data, columns=columns)
        return df
    
    def get_derivative_matched_data(self,start_date, end_date, start_hour, end_hour, time_delay):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        start_hour = datetime.strptime(start_hour, '%H:%M:%S')
        end_hour = datetime.strptime(end_hour, '%H:%M:%S')
        times = []
        prices = []
        tickers = []
        current_date = start_date
        ticketsymbol = 'VN30F2309'
        while current_date <= end_date:
            month = str(current_date.month)
            month = month if len(month) == 2 else '0' + month
            last_2_digits_year = str(current_date.year)[-2:]
            ticketsymbol = 'VN30F' + last_2_digits_year + month
            print("retrieve data in ", current_date.strftime('%Y-%m-%d'), ticketsymbol)
            # query = f'''
            #         SELECT DISTINCT m.datetime as datetime, m.price as price, m.tickersymbol as tickersymbol
            #         FROM quote.matched m 
            #         JOIN quote.futurecontractcode ft 
            #         ON m.tickersymbol=ft.tickersymbol
            #         WHERE ft.futurecode='VN30F1M'
            #         AND m.tickersymbol='{ticketsymbol}'
            #         AND m.datetime > '{start_date.strftime('%Y-%m-%d')} {start_hour.strftime('%H:%M:%S')}'
            #         AND m.datetime < '{end_date.strftime('%Y-%m-%d')} {end_hour.strftime('%H:%M:%S')}'
            #         ORDER BY m.datetime ASC
            #         '''
            query = f'''
                    WITH RankedRows AS (
                    SELECT
                        m.datetime,
                        m.price,
                        LAG(m.datetime) OVER (ORDER BY m.datetime) AS prev_datetime,
                        m.tickersymbol
                    FROM
                        quote.matched m
                    JOIN
                        quote.futurecontractcode ft ON m.tickersymbol = ft.tickersymbol
                    WHERE
                        ft.futurecode = 'VN30F1M'
                        AND m.tickersymbol = '{ticketsymbol}'
                        AND m.datetime >= '{current_date.strftime('%Y-%m-%d')} {start_hour.strftime('%H:%M:%S')}'
                        AND m.datetime <= '{current_date.strftime('%Y-%m-%d')} {end_hour.strftime('%H:%M:%S')}'
                    ORDER BY
                        m.datetime ASC
                    )
                    SELECT
                    datetime,
                    price,
                    tickersymbol
                    FROM
                    RankedRows
                    WHERE
                    prev_datetime IS NULL OR datetime > prev_datetime + INTERVAL '1' SECOND;
            '''
            #                    WHERE
            #                    prev_datetime IS NULL OR datetime > prev_datetime + INTERVAL '1' SECOND;
            self.cursor.execute(query)
            retrieved_data = self.cursor.fetchall()
            

            for data in retrieved_data:
                times.append(data[0])
                prices.append(data[1])
                tickers.append(data[2])
            current_date += timedelta(days=1)
        return pd.DataFrame({'datetime': times, 
                             'price': prices,
                             'tickersymbol': tickers})

    def get_derivative_midprice_data(self,start_date, end_date, start_hour, end_hour, time_delay):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        start_hour = datetime.strptime(start_hour, '%H:%M:%S')
        end_hour = datetime.strptime(end_hour, '%H:%M:%S')
        
        times = []
        bidprices = []
        askprices = []
        tickers = []
        current_date = start_date
        ticketsymbol = 'VN30F2309'
        while current_date <= end_date:
            month = str(current_date.month)
            month = month if len(month) == 2 else '0' + month
            last_2_digits_year = str(current_date.year)[-2:]
            ticketsymbol = 'VN30F' + last_2_digits_year + month
            query = f'''
                    SELECT b.datetime, b.price as bidprice, a.price as askprice, b.tickersymbol
                    FROM quote.bidprice b, quote.askprice a 
                    WHERE b.tickersymbol=a.tickersymbol 
                    AND b.tickersymbol='{ticketsymbol}' 
                    AND b.datetime >= '{current_date.strftime('%Y-%m-%d')} {start_hour.strftime('%H:%M:%S')}'
                    AND b.datetime <= '{current_date.strftime('%Y-%m-%d')} {end_hour.strftime('%H:%M:%S')}'
                    AND b.datetime=a.datetime
                    '''
            # query = f'''
            #         WITH RankedRows AS (
            #         SELECT
            #             b.datetime,
            #             b.price as bidprice,
            #             a.price as askprice,
            #             LAG(b.datetime) OVER (ORDER BY b.datetime) AS prev_datetime,
            #             b.tickersymbol
            #         FROM
            #             quote.bidprice b, quote.askprice a
            #         WHERE
            #             b.tickersymbol=a.tickersymbol
            #             AND b.tickersymbol = '{ticketsymbol}'
            #             AND b.datetime >= '{current_date.strftime('%Y-%m-%d')} {start_hour.strftime('%H:%M:%S')}'
            #             AND b.datetime <= '{current_date.strftime('%Y-%m-%d')} {end_hour.strftime('%H:%M:%S')}'
            #             AND b.datetime=a.datetime
            #         ORDER BY
            #             b.datetime ASC
            #         )
            #         SELECT
            #         datetime,
            #         bidprice,
            #         askprice,
            #         tickersymbol
            #         FROM
            #         RankedRows
            #         WHERE
            #         prev_datetime IS NULL OR datetime > prev_datetime + INTERVAL '{time_delay}' SECOND;
            # '''
            self.cursor.execute(query)
            retrieved_data = self.cursor.fetchall()
            if current_date.day == 13 and current_date.month == 1 and len(retrieved_data) == 0:
                print("No data in 13th January")
                print(query)
                exit(0)

            for data in retrieved_data:
                times.append(data[0])
                bidprices.append(data[1])
                askprices.append(data[2])
                tickers.append(data[3])
            current_date += timedelta(days=1)
        return pd.DataFrame({'time': times, 
                             'bidprice': bidprices,
                             'askprice': askprices, 
                             'tickersymbol': tickers})

    def get_matched_start_n_end(self, 
                 start_date, 
                 end_date, 
                 start_hour, 
                 end_hour, 
                 time_delay):

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        start_hour = datetime.strptime(start_hour, '%H:%M:%S')
        end_hour = datetime.strptime(end_hour, '%H:%M:%S')
        time_delay = timedelta(seconds=time_delay)
        
        start_datas = []
        end_datas = []
        current_date = start_date
        while current_date <= end_date:
            # 
            query = f'''
                    SELECT m.datetime as start_time, m.price as start_price
                    FROM quote.matched m 
                    JOIN quote.futurecontractcode ft
                    ON m.tickersymbol = ft.tickersymbol
                    WHERE ft.futurecode='VN30F1M'
                    AND m.datetime >= '{current_date.strftime('%Y-%m-%d')} {start_hour.strftime('%H:%M:%S')}'
                    AND m.datetime <= '{current_date.strftime('%Y-%m-%d')} {end_hour.strftime('%H:%M:%S')}'
                    AND (m.datetime::time > '{start_hour}') AND (m.datetime::time < '{str(time_delay + start_hour)}')
                    ORDER BY m.datetime ASC
                    LIMIT 1
                    '''
            self.cursor.execute(query)
            retrieved_start_data = self.cursor.fetchall()

            ## Query end data
            query = f'''
                    SELECT m.datetime as end_time, m.price as end_price
                    FROM quote.matched m
                    JOIN quote.futurecontractcode ft
                    ON m.tickersymbol = ft.tickersymbol
                    WHERE ft.futurecode='VN30F1M'
                    AND m.datetime >= '{current_date.strftime('%Y-%m-%d')} {start_hour.strftime('%H:%M:%S')}'
                    AND m.datetime <= '{current_date.strftime('%Y-%m-%d')} {end_hour.strftime('%H:%M:%S')}'
                    ORDER BY m.datetime DESC
                    LIMIT 1
                     '''
            # query = f'''
            #         SELECT m.datetime as end_time, m.price as end_price
            #         FROM quote.matched m
            #         JOIN quote.futurecontractcode ft
            #         ON m.tickersymbol = ft.tickersymbol
            #         WHERE ft.futurecode='VN30F1M'
            #         AND m.datetime >= '{current_date.strftime('%Y-%m-%d')} {start_hour.strftime('%H:%M:%S')}'
            #         AND m.datetime <= '{current_date.strftime('%Y-%m-%d')} 23:59:00'
            #         AND m.datetime::time > '{end_hour.strftime('%H:%M:%S')}'
            #         ORDER BY m.datetime ASC
            #         LIMIT 1
            # '''
            self.cursor.execute(query)
            retrieved_end_data = self.cursor.fetchall()

            if len(retrieved_start_data) > 0 and len(retrieved_end_data) > 0:
                start_datas.append(retrieved_start_data[0])
                end_datas.append(retrieved_end_data[0])

            current_date += timedelta(days=1)
        
        assert len(start_datas) == len(end_datas), "Start datas and end datas must have the same length"
        start_datas = pd.DataFrame(start_datas, columns=['start_time', 'start_price'])
        end_datas = pd.DataFrame(end_datas, columns=['end_time', 'end_price'])
        datas = pd.concat([start_datas, end_datas], axis=1)
        return self.format_data(datas)

    def format_data(self, df):
        data = df.copy()
        data['start_time'] = pd.to_datetime(data['start_time'])
        data['end_time'] = pd.to_datetime(data['end_time'])
        data['start_price'] = data['start_price'].astype(float)
        data['end_price'] = data['end_price'].astype(float)
        return data

    def close(self):
        self.cursor.close()
        self.connection.close()
    

    def __del__(self):
        self.close()

    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    
    