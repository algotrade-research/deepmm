from copy import deepcopy
import numpy as np
import pandas as pd
from src.data.data_type import DataOrder, PositionSide, PriceSize

class HistoricalTickdata():
    def __init__(self):
        self.datetime = np.array([])
        self.price = np.array([])
    
    def append_tick(self, datetime, price):
        self.datetime = np.append(self.datetime, datetime)
        self.price = np.append(self.price, price)

    def export_df_market_timeprice(self, save_file=None):
        datetimes = []
        prices = []
        for (datetime, price) in zip(self.datetime, self.price):
            datetimes.append(datetime)
            prices.append(price)
        df = pd.DataFrame({'datetime': datetimes, 
                           'price': prices})
        if save_file:
            df.to_csv(save_file, index=False)
        return df

class HistoricalOrderDataManagement():
    def __init__(self):
        self.historical_order = []
        self.spread_bid, self.spread_ask = np.array([]), np.array([])
        self.reserv_price = np.array([])
        self.trading_day = []
        self.profit_per_day = np.array([])
        self.market_timeprice = []
        self.num_trade_per_day = np.array([])
        self.inventory_per_day = np.array([])

    def __len__(self):
        return len(self.historical_order)
    

    def calculate_revenue(self, atc_price=0):
        """ This function using for calculate the revenue of the bot with no tax/fee
        """
        revenue = 0
        total_long_size = 0
        total_long_price = 0
        total_short_size = 0
        total_short_price = 0
        for order in self.historical_order:
            if order.position_side == PositionSide.LONG:
                total_long_size += order.price_size.size
                total_long_price += order.price_size.price
            elif order.position_side == PositionSide.SHORT:
                total_short_size += order.price_size.size
                total_short_price += order.price_size.price
        
        if total_long_size == 0:
            total_long_size = 1
        if total_short_size == 0:
            total_short_size = 1        

        avg_price_long = total_long_price / total_long_size
        avg_price_short = total_short_price / total_short_size
        revenue = (atc_price-avg_price_long)*total_long_size + (avg_price_short-atc_price)*total_short_size
        
        return revenue

    def append_order(self, order):
        self.historical_order.append(order)
        
    def append_spread(self, delta_bid, delta_ask):
        self.spread_bid = np.append(self.spread_bid, delta_bid)
        self.spread_ask = np.append(self.spread_ask, delta_ask)

    def append_reserv_price(self, reserv_price):
        self.reserv_price = np.append(self.reserv_price, reserv_price)

    def append_timeprice(self, datetime, price):
        self.market_timeprice.append([datetime, price])

    def append_profit_per_day(self, profit=0, num_trade=0, date=None):
        self.profit_per_day = np.append(self.profit_per_day, profit)
        self.trading_day.append(date)
        self.num_trade_per_day = np.append(self.num_trade_per_day, num_trade)

    def get_data_per_day(self):
        return deepcopy(self.trading_day), deepcopy(self.profit_per_day), deepcopy(self.num_trade_per_day)
    
    def get_list_historical_order(self):
        return [order.to_list() for order in self.historical_order]


    def get_avg_spread(self):
        bid_spread = np.mean(self.spread_bid)
        ask_spread = np.mean(self.spread_ask)
        spread = np.abs(bid_spread - ask_spread)
        return np.mean(spread)
    
    def get_num_order(self):
        return self.__len__()
    
    def get_bidsask_spread(self):
        return self.spread_bid, self.spread_ask

    def get_statistic(self):
        _, profit_per_day, num_trade_per_day = self.get_data_per_day()
        return self.get_avg_spread(), profit_per_day, num_trade_per_day

    def export_df_long_trade(self, save_file=None):
        datetimes = []
        prices = []
        sizes = []
        for order in self.get_list_historical_order():
            if order[3] == PositionSide.LONG:
                datetimes.append(order[0])
                prices.append(order[1])
                sizes.append(order[2])
        df = pd.DataFrame({'datetime': datetimes, 
                           'price': prices, 
                           'size': sizes})
        if save_file:
            df.to_csv(save_file, index=False)
        return df

    def export_df_short_trade(self, save_file=None):
        datetimes = []
        prices = []
        sizes = []
        for order in self.get_list_historical_order():
            if order[3] == PositionSide.SHORT:
                datetimes.append(order[0])
                prices.append(order[1])
                sizes.append(order[2])
        df = pd.DataFrame({'datetime': datetimes, 
                           'price': prices, 
                           'size': sizes})
        if save_file:
            df.to_csv(save_file, index=False)
        return df

    def export_df_profit_per_day(self, save_file=None):
        df = pd.DataFrame({"datetime": self.trading_day, "profit": self.profit_per_day, "num_trade": self.num_trade_per_day})
        if save_file:
            df.to_csv(save_file, index=False)
        return df
    
    def export_df_order(self, save_file=None):
        datetimes = []
        prices = []
        sizes = []
        order_types = []
        for order in self.get_list_historical_order():
            datetimes.append(order[0])
            prices.append(order[1])
            sizes.append(order[2])
            order_types.append(order[3])
        df = pd.DataFrame({'datetime': datetimes, 
                           'price': prices, 
                           'size': sizes, 
                           'order_type': order_types})
        if save_file:
            df.to_csv(save_file, index=False)
        return df