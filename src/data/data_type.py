from decimal import Decimal
from enum import Enum
from typing import (
    List,
    NamedTuple,
)

class Tickdata():
    def __init__(self, datetime=None, price=None):
        self.datetime = datetime
        self.price = price
    
    def is_empty(self):
        if self.datetime is None or self.price is None:
            return True
        return False
    
    def __repr__(self):
        return f"{self.datetime} {self.price}"

class OrderType():
    MARKET = 1
    LIMIT = 2
    LIMIT_MAKER = 3

    def is_limit_type(self):
        return self in (OrderType.LIMIT, OrderType.LIMIT_MAKER)

# For Derivatives Exchanges
class PositionSide():
    LONG = "LONG"
    SHORT ="SHORT"
    BOTH = "BOTH"
    NONE = "None"


# For Derivatives Exchanges
class PositionMode(Enum):
    HEDGE = False
    ONEWAY = True


class PriceType(Enum):
    MidPrice = 1
    BestBid = 2
    BestAsk = 3
    LastTrade = 4
    LastOwnTrade = 5
    InventoryCost = 6
    Custom = 7

class OrdersProposal(NamedTuple):
    actions: int
    buy_order_type: OrderType
    buy_order_prices: List[Decimal]
    buy_order_sizes: List[Decimal]
    sell_order_type: OrderType
    sell_order_prices: List[Decimal]
    sell_order_sizes: List[Decimal]
    cancel_order_ids: List[str]


class PricingProposal(NamedTuple):
    buy_order_prices: List[Decimal]
    sell_order_prices: List[Decimal]


class SizingProposal(NamedTuple):
    buy_order_sizes: List[Decimal]
    sell_order_sizes: List[Decimal]


class InventorySkewBidAskRatios(NamedTuple):
    bid_ratio: float
    ask_ratio: float


class PriceSize:
    def __init__(self, price: Decimal=0, size: Decimal=0):
        self.price: Decimal = price
        self.size: Decimal = size

    def __repr__(self):
        return f"[ p: {self.price} s: {self.size} ]"

class DataOrder:
    def __init__(self,
                 order_id: str="",
                 price_size: PriceSize=PriceSize(),
                 order_type: OrderType=OrderType.MARKET, 
                 position_side: PositionSide=PositionSide.NONE, 
                 datetime: str=""):
        self.order_id  = order_id
        self.price_size = price_size
        self.order_type = order_type
        self.position_side = position_side
        self.datetime = datetime
    
    def is_empty(self):
        return (self.price_size.price == 0 or self.price_size.size == 0 or self.datetime == "" or self.position_side == PositionSide.NONE)

    def __repr__(self):
        return f"Order: {self.datetime} {self.price_size} {self.position_side} {self.order_type}"

    def to_list(self):
        return [self.datetime, self.price_size.price, self.price_size.size, self.position_side, self.order_type]
