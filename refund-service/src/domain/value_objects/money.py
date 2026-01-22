from decimal import Decimal
from typing import Union
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Value object representing monetary amount with currency"""
    amount: Decimal
    currency: str = "USD"  # Default currency

    def __post_init__(self):
        """Validate the money object after initialization"""
        if self.amount < Decimal('0'):
            raise ValueError("Money amount cannot be negative")
        if not isinstance(self.amount, Decimal):
            raise TypeError("Money amount must be a Decimal")

    def __add__(self, other: 'Money') -> 'Money':
        """Add two money objects"""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'Money') -> 'Money':
        """Subtract two money objects"""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        if self.amount < other.amount:
            raise ValueError("Cannot subtract more money than available")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Union[int, float]) -> 'Money':
        """Multiply money by a multiplier"""
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __truediv__(self, divisor: Union[int, float]) -> 'Money':
        """Divide money by a divisor"""
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def format(self) -> str:
        """Format money as string"""
        return f"{self.currency} {self.amount:,.2f}"

    def to_dict(self) -> dict:
        """Convert money to dictionary representation"""
        return {
            "amount": float(self.amount),
            "currency": self.currency
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Money':
        """Create money object from dictionary"""
        return cls(Decimal(str(data["amount"])), data["currency"])

    def __str__(self) -> str:
        return self.format()

    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"