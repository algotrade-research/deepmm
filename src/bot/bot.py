
import numpy as np
import itertools
from tqdm import tqdm
from copy import deepcopy

from src.strategy.asmodel import PureMM
from src.broker.order_management_system import OrderManagementSystem
from src.data.data_type import DataOrder, PriceSize, PositionSide, OrderType, Tickdata
from src.data.inventory_management import InventoryManagement
from src.data.history_management import HistoricalOrderDataManagement, HistoricalTickdata

from utils.date_management import check_stringtime_greater_closetime, \
                                    check_two_stringtime_greater_thresh, \
                                    check_stringtime_less_starttime, \
                                    check_two_string_is_same_day, \
                                    get_maturity_date, \
                                    auto_convert_string_to_datetime

class Bot:
    def __init__(self, opts, logger=None):
        self.opts = opts
        self.close_at = opts['close_at']
        self.start_at = opts['start_at']
        self.historical_window_size = opts['historical_window_size']
        self.time_step = opts['min_second_time_step']

        self._init_capcity()
        self.inventory = InventoryManagement(opts['maximum_inventory'])
        self.history_price = np.array([])
        self.count_history_day = 0
        self.is_waiting_new_day = False


        self.count_order_ids = itertools.count(1)
        self.broker = OrderManagementSystem()
        self.model = PureMM(opts)
        self.previous_tick = Tickdata()
        self.current_tick = Tickdata()
        self.next_tick = Tickdata()
        self.logger = logger

    def _init_capcity(self):
        self.monthly_tick_data = HistoricalTickdata()
        self.total_tick_data = HistoricalTickdata()

        self.monthly_history_data_order = HistoricalOrderDataManagement()
        self.daily_historical_data_order = HistoricalOrderDataManagement()
        self.total_history_data_order = HistoricalOrderDataManagement()
    
    def send_order(self, order, next_tick_price):
        if self.inventory.check_capacity(order) == False:
            return 0
        status = self.broker.send_order(order, next_tick_price)
        if status == 2:
            if order.position_side == PositionSide.LONG:
                self.inventory.increase_inventory()
            elif order.position_side == PositionSide.SHORT:
                self.inventory.decrease_inventory()

            order.update_filled_datetime(order.datetime)
            self.track_order(order)
            self.track_inventory(order.datetime, self.inventory.current_inventory)

            if self.logger:
                type = "Buy" if order.position_side == PositionSide.LONG else "Sell"
                self.logger.info(f"Send {type} Order: {order.order_id} at {order.datetime} with price {order.price_size.price} and size {order.price_size.size}")
        return status

    def check_then_cancel_order(self, datetime, next_tick_price):
        # check waiting order
        for order in self.broker.get_waiting_orders():
            status = self.broker.check_order_status(order, next_tick_price)
            if status == 2:
                
                if order.position_side == PositionSide.LONG:
                    self.inventory.increase_inventory()
                elif order.position_side == PositionSide.SHORT:
                    self.inventory.decrease_inventory()
                order.update_filled_datetime(datetime)
                self.track_order(order)
                self.track_inventory(order.datetime, self.inventory.current_inventory)
                self.broker.send_cancel_order(order.order_id)
                if self.logger:
                    type = "Buy" if order.position_side == PositionSide.LONG else "Sell"
                    self.logger.info(f"Filled {type} Order: {order.order_id} at {order.datetime} with price {order.price_size.price} and size {order.price_size.size}")

        # cancel order if it's not filled and it's over the time step
        for order in self.broker.get_waiting_orders():
            # if check_two_stringtime_greater_thresh(order.datetime, datetime, self.time_step):
            if (datetime-order.datetime).seconds > self.time_step:
                self.broker.send_cancel_order(order.order_id)
                if self.logger:
                    self.logger.info(f"Cancel Order: {order.order_id} at {order.datetime} with price {order.price_size.price} and size {order.price_size.size}")
    
    def track_order(self, order):
        self.monthly_history_data_order.append_order(order)
        self.total_history_data_order.append_order(order)
        self.daily_historical_data_order.append_order(order)
    
    def track_profit(self, profit, num_trade, date):
        self.monthly_history_data_order.append_profit_per_day(profit=profit, num_trade=num_trade, date=date)
        self.total_history_data_order.append_profit_per_day(profit=profit, num_trade=num_trade, date=date)

    def track_inventory(self, datetime, inventory):
        self.daily_historical_data_order.append_inventory(datetime, inventory)
        self.monthly_history_data_order.append_inventory(datetime, inventory)
        self.total_history_data_order.append_inventory(datetime, inventory)

    def track_data(self, datetime, price, delta_bid=0, delta_ask=0, reserv_price=0):
        self.monthly_tick_data.append_tick(datetime, price)
        self.total_tick_data.append_tick(datetime, price)

        # Track Model Spread and Model Reserv Price
        self.monthly_history_data_order.append_spread(delta_bid=delta_bid, delta_ask=delta_ask)
        self.total_history_data_order.append_spread(delta_bid=delta_bid, delta_ask=delta_ask)

        self.monthly_history_data_order.append_reserv_price(reserv_price)
        self.total_history_data_order.append_reserv_price(reserv_price)


    def _auto_close_position(self, datetime:str, 
                                   price:float, 
                                   next_tick_price:float):
        """Auto close position in specific time

        Args:
            datetime (str): time to close position
            price (float): current price
            next_tick_price (float): simulate fill price
        """
        while self.inventory.current_inventory < 0:
            long_order = DataOrder(
                                order_id=next(self.count_order_ids),
                                price_size=PriceSize(price=price, size = 1),
                                position_side=PositionSide.LONG,
                                order_type=OrderType.MARKET,
                                datetime=datetime)
            self.send_order(long_order, next_tick_price)
        
        while self.inventory.current_inventory  > 0:
            short_order = DataOrder(
                                order_id=next(self.count_order_ids),
                                price_size=PriceSize(price=price, size = 1),
                                position_side=PositionSide.SHORT,
                                order_type=OrderType.MARKET,
                                datetime=datetime)
            self.send_order(short_order, next_tick_price)
    
    def init_capacity_every_month(self):
        self.daily_historical_data_order = HistoricalOrderDataManagement()
        self.monthly_history_data_order = HistoricalOrderDataManagement()
        self.monthly_tick_data = HistoricalTickdata()
        self.model.reset()

    def queue_support_tickdata(self, tickdata:Tickdata):
        self.previous_tick = self.current_tick
        self.current_tick = self.next_tick
        self.next_tick = tickdata

    def fit_tickdata(self, tickdata:Tickdata):
        self.queue_support_tickdata(tickdata)
        if self.previous_tick.is_empty() or self.current_tick.is_empty() or self.next_tick.is_empty():
            return

        prev_time = self.previous_tick.datetime
        datetime = auto_convert_string_to_datetime(self.current_tick.datetime)
        price = self.current_tick.price
        next_tick_price = self.next_tick.price

        if not check_two_string_is_same_day(prev_time, datetime):
            self.track_inventory(datetime, self.inventory.current_inventory)
            self.is_waiting_new_day = False

        if check_stringtime_less_starttime(datetime, self.start_at):
                self.track_data(datetime=datetime, price=price, delta_bid=price, delta_ask=price, reserv_price=price)
                if get_maturity_date(datetime) == 20:
                    self.model.set_start_time(datetime)
                    print(f"Start time: {datetime}")
                return
        
        if self.count_history_day < self.historical_window_size:
            self.history_price = np.append(self.history_price, price)
            if check_stringtime_greater_closetime(datetime, self.close_at) and self.is_waiting_new_day == False:
                self.track_inventory(datetime, self.inventory.current_inventory)
                self.count_history_day += 1
                self.is_waiting_new_day = True

            self.track_data(datetime=datetime, price=price, delta_bid=price, delta_ask=price, reserv_price=price)
            return
        if check_stringtime_greater_closetime(datetime, self.close_at):
            ## It's closing time at end day
            self._auto_close_position(datetime, price, next_tick_price)
            self.track_data(datetime=datetime, price=price, delta_bid=price, delta_ask=price, reserv_price=price)
            # Take End day profit
            if self.inventory.current_inventory == 0 and not self.is_waiting_new_day:
                atc_price = price
                end_day_profit = self.daily_historical_data_order.calculate_revenue(atc_price)
                num_trade = self.daily_historical_data_order.get_num_order()
                self.track_profit(end_day_profit, num_trade, datetime)
                self.track_inventory(datetime, self.inventory.current_inventory)

                self.daily_historical_data_order = HistoricalOrderDataManagement()
                self.broker.clear_waiting_orders()
                self.is_waiting_new_day = True
            return
        
        if len(self.history_price) != 0:
            self.history_price[:-1] = self.history_price[1:]; self.history_price[-1] = price # assign new tickdata arrival into history price
        delta_bid, delta_ask, reserv_price = self.model.signal(datetime=datetime, 
                                                                price=price, 
                                                                inventory=self.inventory.previous_inventory,
                                                                history_price=self.history_price)

        self.check_then_cancel_order(datetime, next_tick_price)

        if delta_bid != 0:
            delta_bid = round(delta_bid, 1)
            long_order = DataOrder(
                                    order_id=next(self.count_order_ids),    
                                    price_size=PriceSize(price=delta_bid, size = 1),
                                    position_side=PositionSide.LONG,
                                    order_type=OrderType.LIMIT,
                                    datetime=datetime)
            if self.broker.previous_orders.is_empty():
                self.send_order(long_order, next_tick_price)
            elif (datetime-self.broker.previous_orders.datetime).seconds > self.time_step:
                self.send_order(long_order, next_tick_price)
        
        if delta_ask != 0:
            delta_ask = round(delta_ask, 1)
            short_order = DataOrder(
                                    order_id=next(self.count_order_ids),
                                    price_size=PriceSize(price=delta_ask, size = 1),
                                    position_side=PositionSide.SHORT,
                                    order_type=OrderType.LIMIT,
                                    datetime=datetime)
            if self.broker.previous_orders.is_empty():
                self.send_order(short_order, next_tick_price)
            elif (datetime-self.broker.previous_orders.datetime).seconds > self.time_step:
                self.send_order(short_order, next_tick_price)

        self.track_data(datetime, price, delta_bid, delta_ask, reserv_price)

    def fit(self, datasets):
        self.init_capacity_every_month()
        for t , (datetime, price) in tqdm(enumerate(datasets, start=0), desc="Fitting offline data"):
            self.fit_tickdata(Tickdata(datetime, price))
    
    def get_daily_history(self):
        return deepcopy(self.daily_historical_data_order)

    def get_monthly_history(self):
        return deepcopy(self.monthly_history_data_order)
    
    def get_total_history(self):
        return deepcopy(self.total_history_data_order)