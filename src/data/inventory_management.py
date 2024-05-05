import pandas as pd

from copy import deepcopy
from src.data.data_type import DataOrder, PositionSide, PriceSize

class InventoryManagement():
    def __init__(self, maximum_inventory):
        self.maximum_inventory = maximum_inventory-1
        self.current_inventory = 0
        self.previous_inventory = 0
    
    def increase_inventory(self, num_contract=1):
        self.previous_inventory = self.current_inventory
        self.current_inventory += num_contract
    
    def decrease_inventory(self, num_contract=1):
        self.previous_inventory = self.current_inventory
        self.current_inventory -= num_contract

    def get_maximum_inventory(self):
        return deepcopy(self.maximum_inventory)

    def init_inventory(self):
        self.current_inventory = 0

    