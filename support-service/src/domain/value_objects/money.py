from decimal import Decimal
from typing import Optional


class Money:
    """Value object representing monetary values consistently"""

    def __init__(self, amount: Decimal, currency: str = "EUR"):
        if amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        self.amount = amount
        self.currency = currency

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add Money in different currencies")
        
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract Money in different currencies")
        
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: float) -> "Money":
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

    def __repr__(self) -> str:
        return f"<Money {self.currency} {self.amount}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency