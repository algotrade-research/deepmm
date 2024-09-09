from copy import deepcopy
from deepmm.data.data_type import DataOrder, PositionSide, OrderType

class OrderManagementSystem:
    def __init__(self):
        self.waiting_orders = []
        self.filled_orders = []
        self.previous_orders = DataOrder()

    def get_waiting_orders(self):
        return deepcopy(self.waiting_orders)

    def send_order(self, order: DataOrder, next_tick_price=0):
        """ Send order to the broker
            currently, it only simulate the order

            return:
                0: order is not valid
                1: order is waiting
                2: order is filled
        """
        if order.is_empty():
            return 0
        
        if order.order_type == OrderType.LIMIT:
            if order.position_side == PositionSide.LONG and next_tick_price < order.price_size.price:
                self.previous_orders = order
                return 2
            elif order.position_side == PositionSide.SHORT and next_tick_price > order.price_size.price:
                self.previous_orders = order
                return 2
            else:
                self.waiting_orders.append(order)
                return 1

        if order.order_type == OrderType.MARKET:
            return 2
        return 0

    def send_cancel_order(self, order_id):
        for i, order in enumerate(self.waiting_orders):
            if order.order_id == order_id:
                self.waiting_orders.pop(i)
                return True
        return False
    
    def check_order_status(self, order, next_tick_price):
        if order.position_side == PositionSide.LONG and next_tick_price < order.price_size.price:
            return 2
        elif order.position_side == PositionSide.SHORT and next_tick_price > order.price_size.price:
            return 2
        return 1

    def clear_waiting_orders(self):
        self.waiting_orders = []