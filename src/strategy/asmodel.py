from typing import Any
import numpy as np
import math
from utils.date_management import get_num_days_to_maturity, make_date_to_tickersymbol, get_maturity_date_from_symbol

class PureMM:
    def __init__(self, opts):
        # Parameters for mid price simulation:
        self.T = 1            			# time
        self.gamma = opts['gamma'] 		# risk aversion
        self.k = 1.5				# probability of market order arrival
        self.historical_window_size = opts['historical_window_size']
        self.num_of_spread = opts['num_of_spread']
    
    def reset_T(self):
        self.T = 1

    def signal(self, datetime, price, inventory, history_price):
        self.T = self.T - 2.5e-5
        if self.T < 0:
            self.T = 0

        # calculate volatility
        sigma = np.std(history_price)
        s = price
        reserv_price = s - inventory.previous_inventory * self.gamma * (sigma ** 2) * (self.T)						 # Mid Price estimation
        spread = self.gamma * (sigma ** 2) * (self.T) + (2/self.gamma) * math.log(1 + (self.gamma/self.k))	 # Spread estimation

        delta_bid = reserv_price - (spread/2.0 * self.num_of_spread)		# bid
        delta_ask = reserv_price + (spread/2.0 * self.num_of_spread)		# ask
        
        return delta_bid, delta_ask, reserv_price

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   