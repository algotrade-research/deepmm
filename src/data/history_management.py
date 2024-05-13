from copy import deepcopy
import numpy as np
import pandas as pd
from src.data.data_type import PositionSide
from utils.date_management import make_date_from_string

class HistoricalTickdata():
    def __init__(self):
        self.size = 0
        self.datetime = []
        self.price = []
    
    def get_hictory_tick(self):
        return np.array(self.datetime), np.array(self.price)

    def append_tick(self, datetime, price):
        self.datetime.append(datetime)
        self.price.append(price)

    def export_df_market_timeprice(self, save_file=None):
        datetimes = []
        prices = []
        datetime, price = self.get_hictory_tick()
        for (datetime, price) in zip(datetime, price):
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
        self.spread_bid, self.spread_ask = [], []
        self.reserv_price = []
        self.trading_day = []
        self.profit_per_day = []
        self.market_timeprice = []
        self.num_trade_per_day = []
        self.track_inventory = []

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
        self.spread_bid.append(delta_bid)
        self.spread_ask.append(delta_ask)

    def append_reserv_price(self, reserv_price):
        self.reserv_price.append(reserv_price)

    def append_timeprice(self, datetime, price):
        self.market_timeprice.append([datetime, price])

    def append_profit_per_day(self, profit=0, num_trade=0, date=None):
        self.profit_per_day.append(profit)
        self.trading_day.append(date)
        self.num_trade_per_day.append(num_trade)

    def append_inventory(self, datetime, num_inventory):
        self.track_inventory.append([datetime, num_inventory])

    def get_data_per_day(self):
        return deepcopy(self.trading_day), deepcopy(np.array(self.profit_per_day)), deepcopy(np.array(self.num_trade_per_day))
    
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
                           'position_side': order_types})
        if save_file:
            df.to_csv(save_file, index=False)
        return df
    
    def export_df_order_analysis(self, fees=0, save_file=None):
        list_order_position = deepcopy(self.historical_order)
        
        open_times = []
        close_times = []
        open_prices = []
        close_prices = []
        open_sides = []
        close_sides = []
        profits = []
        durations = []

        while len(list_order_position) > 0:
            open_order = list_order_position.pop(0)
            for close_order in list_order_position:
                if close_order.position_side != open_order.position_side:
                    open_times.append(open_order.datetime)
                    open_prices.append(open_order.price_size.price)
                    close_times.append(close_order.datetime)
                    close_prices.append(close_order.price_size.price)
                    open_sides.append(open_order.position_side)
                    close_sides.append(close_order.position_side)
                    profit = (close_order.price_size.price - open_order.price_size.price) * open_order.price_size.size - fees*2
                    if open_order.position_side == PositionSide.SHORT:
                        profit = (open_order.price_size.price - close_order.price_size.price) * open_order.price_size.size - fees*2
                    profits.append(profit)
                    durations.append((make_date_from_string(close_order.datetime) - make_date_from_string(open_order.datetime)).total_seconds())
                    list_order_position.remove(close_order)
                    break
        
        df = pd.DataFrame({
        "open_time": open_times,
        "close_time": close_times,
        "duration": durations,
        "open_price": open_prices,
        "close_price": close_prices,
        "profit": profits,
        "open_side": open_sides,
        "close_side": close_sides,
        })
            
        if save_file:
            df.to_csv(save_file, index=False)
        return df
    
    def export_df_inventory(self, save_file=None):
        datetimes = []
        inventory = []
        for track in self.track_inventory:
            datetimes.append(track[0])
            inventory.append(track[1])
        df = pd.DataFrame({'datetime': datetimes, 
                           'inventory': inventory})
        if save_file:
            df.to_csv(save_file, index=False)
        return df