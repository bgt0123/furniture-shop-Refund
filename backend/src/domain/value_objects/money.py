"""Money value object."""

from decimal import Decimal
from typing import Any


class Money:
    """Money value object with currency support."""

    def __init__(self, amount: Decimal, currency: str = "USD"):
        if amount < Decimal("0"):
            raise ValueError("Amount cannot be negative")
        if not currency:
            raise ValueError("Currency cannot be empty")

        self.amount = amount
        self.currency = currency.upper()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        if self.amount < other.amount:
            raise ValueError("Resulting amount cannot be negative")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Decimal) -> "Money":
        return Money(self.amount * multiplier, self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

    def to_dict(self) -> dict:
        return {"amount": float(self.amount), "currency": self.currency}
