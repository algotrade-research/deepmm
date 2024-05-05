# from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

from src.data.history_management import HistoricalOrderDataManagement


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
                               model,
                               bot_data: HistoricalOrderDataManagement,
                               save_dir: str,
                               symbol: str):
        """
        args:
            monthly_data: numpy_list of monthly data
            bot_data: list of bot data
        """
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(f"{save_dir}/{symbol}", exist_ok=True)

        
        # Create a DataFrame
        df = bot_data.export_df_market_timeprice()
        df_long_trade = bot_data.export_df_long_trade()
        df_short_trade = bot_data.export_df_short_trade()

        df_order = bot_data.export_df_order()
        if save_dir:
            df_order.to_csv(f"{save_dir}/{symbol}/{symbol}_monthly_order.csv")
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
            fig.write_html(f"{save_dir}/{symbol}/{symbol}_monthly_trend.html")
        
        df_profit = bot_data.export_df_profit_per_day(save_file=f"{save_dir}/{symbol}/{symbol}_monthly_profit.csv")
        profit_after_fee = df_profit['profit'] - df_profit['num_trade']*self.fees
        df_profit['profit_after_fee'] = profit_after_fee
        fig_profig = go.Figure()
        fig_profig.add_trace(go.Bar(x=df_profit['datetime'], y=df_profit['profit'], name='Profit Without Trading Fee', marker_color='blue'))
        fig_profig.add_trace(go.Bar(x=df_profit['datetime'], y=df_profit['profit_after_fee'], name='Profit After Fee', marker_color='green'))
        fig_profig.write_html(f"{save_dir}/{symbol}/{symbol}_monthly_profit.html")


        # Visualize Spread

        bids, asks = bot_data.get_bidsask_spread()

        datetime = df['datetime']
        df_spread = pd.DataFrame({ "datetime": datetime,
                                   "ask": asks,
                                  "bid": bids})
        
        def remove_zero_value(df):
            return df[(df['ask'] != 0) & (df['bid'] != 0)]

        fitlered_df = remove_zero_value(df_spread.copy())
        if save_dir:
            df_spread.to_csv(f"{save_dir}/{symbol}/{symbol}_monthly_ask_bid.csv")
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
            fig_ask_bid.write_html(f"{save_dir}/{symbol}/{symbol}_monthly_ask_bid.html")