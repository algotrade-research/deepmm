from src.data.data_type import DataOrder, PriceSize, PositionSide, OrderType

class OrderManagementSystem:
    def __init__(self):
        pass

    

    def send_order(self, order, next_tick_price=0):
        """ Send order to the broker
            currently, it only simulate the order

            return:
                0: order is not valid
                1: order is waiting
                2: order is filled
        """

        if not order.is_valid_to_post_order():
            return 0
        
        if order.order_type == OrderType.LIMIT:
            if order.position_side == PositionSide.LONG and next_tick_price < order.price_size.price:
                return 2
            elif order.position_side == PositionSide.SHORT and next_tick_price > order.price_size.price:
                return 2
            else:
                return 1

        if order.order_type == OrderType.MARKET:
            return 2

        return 0
        
        
    

    def send_cancel_order(self, order_id):
        pass