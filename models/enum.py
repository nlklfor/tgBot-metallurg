from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
