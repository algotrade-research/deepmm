# from matplotlib import pyplot as plt
import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

import plotly.subplots

from src.data.history_management import HistoricalOrderDataManagement, HistoricalTickdata


class VISUALIZER():

    def __init__(self, fees: float) -> None:
        self.fees = fees

    def visualize_total_data(self, total_data, save_dir: str, name="bruh"):
        os.makedirs(save_dir, exist_ok=True)

        profit_df = total_data.export_df_profit_per_day()
        profit = profit_df['profit'].to_numpy()
        pnl_accum = np.cumsum(profit)
        # fig = go.Figure(data=go.Scatter(x=profit_df['datetime'], y=pnl_accum), layout_title_text="PnL Accumulation Without Trading Fee", 
        #                                             layout_xaxis_title="Day", layout_yaxis_title="PnL")
        fig = go.Figure()
        
        num_trade = profit_df['num_trade'].to_numpy()
        profit_after_fee = profit - num_trade*self.fees
        pnl_accum_after_fee = np.cumsum(profit_after_fee)

        fig.add_trace(go.Scatter(x=profit_df['datetime'], y=pnl_accum, mode='lines', name='PnL Accumulation Without Trading Fee', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=profit_df['datetime'], y=pnl_accum_after_fee, mode='lines', name='PnL Accumulation After Trading Fee', line=dict(color='green')))
        fig.update_layout(title=name)
        fig.write_html(f"{save_dir}/pnl_accum.html")

    def visualize_monthly_data(self, 
                               bot_data:HistoricalOrderDataManagement,
                               bot_data_market_time_price: HistoricalTickdata,
                               symbol: str,
                               save_dir: str,):
        """
        args:
            monthly_data: numpy_list of monthly data
            bot_data: list of bot data
        """
        self.visualize_trend_order(bot_data, bot_data_market_time_price, symbol, save_dir)
        self.visualize_profit(bot_data, symbol, save_dir)
        self.visualize_bid_ask_spread(bot_data, bot_data_market_time_price, symbol, save_dir)
        self.visualize_inventory(bot_data, symbol, save_dir)
        self.visualize_table_order_analysis(bot_data, save_dir/symbol)

    def visualize_table_order_analysis(self, bot_data:HistoricalOrderDataManagement, save_dir:str):
        df_order_analysis = bot_data.export_df_order_analysis()
        df_order_analysis = df_order_analysis.round(2)


        for i, row in df_order_analysis.iterrows():
            df_order_analysis.loc[i,'open_time'] = row['open_time'][:-4]
            df_order_analysis.loc[i,'filled_open_time'] = row['filled_open_time'][:-4]
            df_order_analysis.loc[i,'close_time'] = row['close_time'][:-4]
            df_order_analysis.loc[i,'filled_close_time'] = row['filled_close_time'][:-4]
       
        os.makedirs(save_dir, exist_ok=True)
        fig_order = plotly.subplots.make_subplots(rows=2, cols=1,
                                                  shared_xaxes=True,
                                                  specs=[[{'type':'table'}],
                                                         [{'type':'table'}]])

        fig_order.add_trace(go.Table(header=dict(values=list(df_order_analysis.columns)),
                                    cells=dict(values=df_order_analysis.transpose().values.tolist())),
                                    row=1, col=1)
        
        df_describe = df_order_analysis[['duration', 'filled_duration', 'profit']].describe()
        df_describe = df_describe.round(2)

        df_describe_column_name = df_describe.index.name
        df_describe_index_values = df_describe.index

        df_describe.insert(loc=0, column=df_describe_column_name, value=df_describe_index_values)
        fig_order.add_trace(go.Table(header = dict(values=df_describe.columns.tolist()),
                                     cells=dict(values = df_describe.transpose().values.tolist())),
                                     row=2,col=1)
        fig_order.update_layout(title='Order Analysis')
        if save_dir:
            fig_order.write_html(f"{save_dir}/order_analysis.html")
    
    def visualize_inventory(self, 
                            bot_data:HistoricalOrderDataManagement,
                            symbol:str,
                            save_dir:str):
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(f"{save_dir}/{symbol}", exist_ok=True)

        df_inventory = bot_data.export_df_inventory()
        fig_inventory = go.Figure()
        fig_inventory.add_trace(go.Scatter(x=df_inventory['datetime'], 
                                       y=df_inventory['inventory'], 
                                        mode='lines+markers',
                                       name='Inventory', 
                                       marker=dict(color='blue', size=15)))
        
        fig_inventory.update_layout(title='Inventory Management',
                                    xaxis_title='Date',
                                    yaxis_title='Inventory')
        if save_dir:
            fig_inventory.write_html(f"{save_dir}/{symbol}/{symbol}_inventory.html")

    def visualize_trend_order(self,
                              bot_data:HistoricalOrderDataManagement,
                              bot_data_market_timeprice: HistoricalTickdata,
                              symbol: str,
                              save_dir:str):
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(f"{save_dir}/{symbol}", exist_ok=True)

        # Create a DataFrame
        df = bot_data_market_timeprice.export_df_market_timeprice()
        df_long_trade = bot_data.export_df_long_trade()
        df_short_trade = bot_data.export_df_short_trade()

        bot_data.export_df_order()
        # Create the line chart with Plotly
        fig = go.Figure(
            data=[go.Scatter(
                    x=df['datetime'],
                    y=df['price'],
                    mode='lines',  # Line chart
                    name='Tick Price'
                )]
        )
        fig.add_trace(
            go.Scatter(
                x=df_long_trade['datetime'],
                y=df_long_trade['price'],
                mode='markers',  # Use markers to distinguish from the line
                name='Long Trade',
                marker=dict(color='green', size=10)
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df_short_trade['datetime'],
                y=df_short_trade['price'],
                mode='markers',  # Use markers to distinguish from the line
                name='Short Trade',
                marker=dict(color='red',size=10)
            )
        )

        # Customize the chart appearance
        fig.update_layout(
            title='Monthly Tick Price Trend',
            xaxis_title='Date',
            yaxis_title='Tick Price',
            xaxis_type='date'  # Set x-axis as date type
        )

        # Display the chart
        if save_dir:
            fig.write_html(f"{save_dir}/{symbol}/{symbol}_trend.html")

    def visualize_profit(self,  
                         bot_data:HistoricalOrderDataManagement,
                         symbol:str,
                         save_dir:str,):
        
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(f"{save_dir}/{symbol}", exist_ok=True)
        df_profit = bot_data.export_df_profit_per_day()
        profit_after_fee = df_profit['profit'] - df_profit['num_trade']*self.fees
        df_profit['profit_after_fee'] = profit_after_fee
        fig_profig = go.Figure()
        fig_profig.add_trace(go.Bar(x=df_profit['datetime'], y=df_profit['profit'], name='Profit Without Trading Fee', marker_color='blue'))
        fig_profig.add_trace(go.Bar(x=df_profit['datetime'], y=df_profit['profit_after_fee'], name='Profit After Fee', marker_color='green'))
        if save_dir:
            fig_profig.write_html(f"{save_dir}/{symbol}/{symbol}_profit.html")

    def visualize_bid_ask_spread(self,
                                 bot_data:HistoricalOrderDataManagement,
                                 bot_data_market_timeprice:HistoricalTickdata, 
                                 symbol: str,
                                 save_dir: str):
        # Visualize Spread
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(f"{save_dir}/{symbol}", exist_ok=True)
        bids, asks = bot_data.get_bidsask_spread()
        df = bot_data_market_timeprice.export_df_market_timeprice()
        df_long_trade = bot_data.export_df_long_trade()
        df_short_trade = bot_data.export_df_short_trade()
        
        datetime = df['datetime']
        df_spread = pd.DataFrame({"datetime": datetime,
                                   "ask": asks,
                                  "bid": bids})
        
        def remove_zero_value(df):
            return df[(df['ask'] != 0) & (df['bid'] != 0)]

        fitlered_df = remove_zero_value(df_spread.copy())

        fig_ask_bid = go.Figure()
        fig_ask_bid.add_trace(go.Scatter(x=df['datetime'], y=df['price'], mode='lines', name='Tick Prices'))
        fig_ask_bid.add_trace(go.Scatter(x=fitlered_df['datetime'], y=fitlered_df['ask'], mode='lines', name='Ask', line=dict(color='red')))
        fig_ask_bid.add_trace(go.Scatter(x=fitlered_df['datetime'], y=fitlered_df['bid'], mode='lines', name='Bid', line=dict(color='green')))

        fig_ask_bid.add_trace(
            go.Scatter(
                x=df_long_trade['datetime'],
                y=df_long_trade['price'],
                mode='markers',  # Use markers to distinguish from the line
                name='Long Trade',
                marker=dict(color='green', size=20)
            )
        )

        fig_ask_bid.add_trace(
            go.Scatter(
                x=df_short_trade['datetime'],
                y=df_short_trade['price'],
                mode='markers',  # Use markers to distinguish from the line
                name='Short Trade',
                marker=dict(color='red',size=20)
            )
        )
        
        if save_dir:
            fig_ask_bid.write_html(f"{save_dir}/{symbol}/{symbol}_ask_bid.html")