from typing import Any
import numpy as np
import math


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

    def signal(self, datetime:str, 
                     price:float, 
                     inventory: int, 
                     history_price: np.ndarray) -> tuple:
        """_summary_

        Args:
            datetime (str): datetime of the current price
            price (float): current price
            inventory (int): inventory of the agent
            history_price (np.ndarray): array of historical prices

        Returns:
            tuple: (delta_bid, delta_ask, reserv_price)
            which delta_bid is the bid price, 
            delta_ask is the ask price, 
            and reserv_price is the reservation price
        """
        
        # if self.start_time is None:
        #     self.start_time = datetime
        #     return 0, 0, 0
        # self.counter += 1
        # lambda_ = calculate_distance_milis(datetime, self.start_time)/self.counter
        # T_prime = self._calculate_new_T(self.counter, lambda_)
        # self.T = min(self.T, T_prime)
        # if self.T < 0:
        #     self.T = 0
        # calculate volatility
        
        self.T -= 2.5e-5
        if self.T < 0:
            self.T = 1e-6
        sigma = np.std(history_price)
        s = price
        reserv_price = s - inventory * self.gamma * (sigma ** 2) * (self.T)						 # Mid Price estimation
        spread = self.gamma * (sigma ** 2) * (self.T) + (2/self.gamma) * math.log(1 + (self.gamma/self.k))	 # Spread estimation
        spread = spread / 2.0
        delta_bid = reserv_price - (spread * self.num_of_spread)		# bid
        delta_ask = reserv_price + (spread * self.num_of_spread)		# ask
        
        return delta_bid, delta_ask, reserv_price

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   