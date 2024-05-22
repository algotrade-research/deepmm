from typing import Any
import numpy as np
import math

from utils.date_management import calculate_distance_milis

class PureMM:
    def __init__(self, opts):
        # Parameters for mid price simulation:
        self.T = 1            			# time
        self.gamma = opts['gamma'] 		# risk aversion
        self.k = 1.5				# probability of market order arrival
        self.historical_window_size = opts['historical_window_size']
        self.num_of_spread = opts['num_of_spread']
        self.counter = 0
        self.start_time = None
    
    def set_start_time(self, start_time):
        self.start_time = start_time
    
    def reset(self):
        self.T = 1
        self.counter = 1
        
    def _calculate_new_T(self, counter, lambda_):
        T_prime = lambda_ / (lambda_ + counter)
        return T_prime

    def signal(self, datetime, price, inventory, history_price):
        if self.start_time is None:
            self.start_time = datetime
            return 0, 0, 0
        self.counter += 1
        lambda_ = calculate_distance_milis(datetime, self.start_time)/self.counter
        T_prime = self._calculate_new_T(self.counter, lambda_)
        self.T = min(self.T, T_prime)
        if self.T < 0:
            self.T = 0
        # calculate volatility
        sigma = np.std(history_price)
        s = price
        reserv_price = s - inventory.previous_inventory * self.gamma * (sigma ** 2) * (self.T)						 # Mid Price estimation
        spread = self.gamma * (sigma ** 2) * (self.T) + (2/self.gamma) * math.log(1 + (self.gamma/self.k))	 # Spread estimation
        spread = spread / 2.0
        delta_bid = reserv_price - (spread * self.num_of_spread)		# bid
        delta_ask = reserv_price + (spread * self.num_of_spread)		# ask
        
        return delta_bid, delta_ask, reserv_price

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   