from copy import deepcopy
import numpy as np

from src.strategy.asmodel import PureMM
from src.broker.order_management_system import OrderManagementSystem
from src.data.data_type import DataOrder, PriceSize, PositionSide, OrderType
from src.data.inventory_management import InventoryManagement
from src.data.history_management import HistoricalOrderDataManagement

from utils.date_management import check_stringtime_greater_closetime, \
                                    check_two_stringtime_greater_thresh, \
                                    check_stringtime_less_starttime, \
                                    check_two_string_is_same_day

class Backtest:
    def __init__(self, opts):
        self.opts = opts
        self.close_at = opts['close_at']
        self.start_at = opts['start_at']
        self.historical_window_size = opts['historical_window_size']
        self.time_step = opts['min_second_time_step']
        self.inventory = InventoryManagement(opts['maximum_inventory'])
        self._init_capcity()

        self.broker = OrderManagementSystem()

        self.model = PureMM(opts)

    def _init_capcity(self):
        self.monthly_history_data_order = HistoricalOrderDataManagement()
        self.daily_historical_data_order = HistoricalOrderDataManagement()
        self.total_history_data_order = HistoricalOrderDataManagement()
    
    def send_order(self, order, next_tick_price):
        status = self.broker.send_order(order, next_tick_price)
        if status == 2:
            if order.position_side == PositionSide.LONG:
                self.inventory.increase_inventory(order.price_size.size)
            elif order.position_side == PositionSide.SHORT:
                self.inventory.decrease_inventory(order.price_size.size)
            
            self.track_order(order)

    def track_order(self, order):
        self.monthly_history_data_order.append_order(order)
        self.total_history_data_order.append_order(order)
        self.daily_historical_data_order.append_order(order)
    
    def track_profit(self, profit, num_trade, date):
        self.monthly_history_data_order.append_profit_per_day(profit=profit, num_trade=num_trade, date=date)
        self.total_history_data_order.append_profit_per_day(profit=profit, num_trade=num_trade, date=date)

    def track_data(self, datetime, price, delta_bid, delta_ask, reserv_price):
        # Track Market PriceTime
        self.monthly_history_data_order.append_timeprice(datetime=datetime,
                                                         price=price)
     
        self.total_history_data_order.append_timeprice(datetime=datetime,
                                                       price=price)
        
        # Track Model Spread and Model Reserv Price
        self.monthly_history_data_order.append_spread(delta_bid=delta_bid, delta_ask=delta_ask)
        self.total_history_data_order.append_spread(delta_bid=delta_bid, delta_ask=delta_ask)

        self.monthly_history_data_order.append_reserv_price(reserv_price)
        self.total_history_data_order.append_reserv_price(reserv_price)


    def _auto_close_position(self, price, datetime, next_tick_price):
        # and next_tick_price < price
        while self.inventory.current_inventory < 0:
            long_order = DataOrder(price_size=PriceSize(price=price, size = 1),
                                position_side=PositionSide.LONG,
                                order_type=OrderType.LIMIT,
                                datetime=datetime)
            self.send_order(long_order, next_tick_price)
        
        # and next_tick_price > price
        while self.inventory.current_inventory  > 0:
            short_order = DataOrder(price_size=PriceSize(price=price, size = 1),
                                position_side=PositionSide.SHORT,
                                order_type=OrderType.LIMIT,
                                datetime=datetime)
            self.send_order(short_order, next_tick_price)
    
    
    def fit(self, datasets):
        count_history_day = 0
        is_waiting_new_day = False

        history_price = np.array([])
        prev_time = datasets[0][0]

        next_tick_price = datasets[2][1]
        for t , (datetime, price) in enumerate(datasets[:-1], start=0):
            next_tick_price = datasets[t+1][1]
            if check_stringtime_less_starttime(datetime, self.start_at):
                continue

            if count_history_day < self.historical_window_size:
                history_price = np.append(history_price, price)
                if check_stringtime_greater_closetime(datetime, self.close_at):
                    count_history_day += 1
                continue

            if check_stringtime_greater_closetime(datetime, self.close_at):
                ## It's closing time at end day
                self._auto_close_position(price, datetime, next_tick_price)

                # Take End day profit
                if self.inventory.current_inventory == 0 and not is_waiting_new_day:
                    atc_price = price
                    end_day_profit = self.daily_historical_data_order.calculate_revenue(atc_price)
                    num_trade = self.daily_historical_data_order.get_num_order()
                    self.track_profit(end_day_profit, num_trade, datetime)

                    self.daily_historical_data_order = HistoricalOrderDataManagement()
                    is_waiting_new_day = True
                continue

            if not check_two_string_is_same_day(prev_time, datetime):
                is_waiting_new_day = False
            
            delta_bid, delta_ask, reserv_price = self.model.signal(datetime=datetime, 
                                                                   price=price, 
                                                                   inventory=self.inventory,
                                                                   history_price=history_price)

            if delta_bid != 0 and check_two_stringtime_greater_thresh(prev_time, datetime, self.time_step):
                long_order = DataOrder(price_size=PriceSize(price=delta_bid, size = 1),
                                        position_side=PositionSide.LONG,
                                        order_type=OrderType.LIMIT,
                                        datetime=datetime)
                self.send_order(long_order, next_tick_price)
            
            if delta_ask != 0 and check_two_stringtime_greater_thresh(prev_time, datetime, self.time_step):
                short_order = DataOrder(price_size=PriceSize(price=delta_ask, size = 1),
                                        position_side=PositionSide.SHORT,
                                        order_type=OrderType.LIMIT,
                                        datetime=datetime)
                self.send_order(short_order, next_tick_price)

            self.track_data(datetime, price, delta_bid, delta_ask, reserv_price)
            prev_time = datetime
    
    def get_monthly_history(self):
        return deepcopy(self.monthly_history_data_order)
    
    def get_total_history(self):
        return deepcopy(self.total_history_data_order)