"""Domain entities module."""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import entities to ensure they are registered with Base
from .support_case import SupportCase
from .refund_case import RefundCase
from .refund_item import RefundItem
from .customer import Customer
from .support_agent import SupportAgent
from .order_reference import OrderReference
