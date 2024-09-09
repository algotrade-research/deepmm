from copy import deepcopy
from deepmm.data.data_type import DataOrder, PositionSide


class InventoryManagement():
    def __init__(self, maximum_inventory):
        self.maximum_inventory = maximum_inventory-1
        self.current_inventory = 0
        self.previous_inventory = 0
    
    def increase_inventory(self, num_contract=1):
        self.previous_inventory = self.current_inventory
        self.current_inventory += num_contract
    
    def decrease_inventory(self, num_contract=1):
        if num_contract > 0:
            num_contract = -num_contract
        self.previous_inventory = self.current_inventory
        self.current_inventory += num_contract

    def get_maximum_inventory(self):
        return deepcopy(self.maximum_inventory)

    def init_inventory(self):
        self.current_inventory = 0

    def check_capacity(self, order: DataOrder):
        if order.position_side == PositionSide.LONG:
            if self.current_inventory + order.price_size.size > self.maximum_inventory:
                return False
        elif order.position_side == PositionSide.SHORT:
            if self.current_inventory - order.price_size.size < -self.maximum_inventory:
                return False
        return True

    