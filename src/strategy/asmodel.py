from typing import Any
import numpy as np
import math
from copy import deepcopy

from utils.date_management import check_stringtime_greater_closetime, \
                                    check_two_stringtime_greater_thresh, \
                                    check_stringtime_less_starttime, \
                                    check_two_string_is_same_day
from src.data.data_type import DataOrder, PriceSize, PositionSide, OrderType

from src.data.history_management import HistoricalOrderDataManagement


class PureMM:
    def __init__(self, opts):
        # Parameters for mid price simulation:

        self.time_step = opts['min_second_time_step']
        self.T = 1            			# time
        self.gamma = opts['gamma'] 		# risk aversion
        self.k = 1.5				# probability of market order arrival
        self.historical_window_size = opts['historical_window_size']
        self.num_of_spread = opts['num_of_spread']

        self.prev_time = None

    def signal(self, datetime, price, inventory, history_price):
        # calculate volatility

        sigma = np.std(history_price)

        if self.T < 0:
            self.T = 0.0001
        else:
            self.T -= 0.0001

        s = price
        reserv_price = s - inventory.previous_inventory * self.gamma * (sigma ** 2) * (self.T)						 # Mid Price estimation
        spread = self.gamma * (sigma ** 2) * (self.T) + (2/self.gamma) * math.log(1 + (self.gamma/self.k))	 # Spread estimation

        delta_bid = reserv_price - (spread/2.0 * self.num_of_spread)		# bid
        delta_ask = reserv_price + (spread/2.0 * self.num_of_spread)		# ask
        
        return delta_bid, delta_ask, reserv_price

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   