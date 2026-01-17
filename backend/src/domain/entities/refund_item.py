"""RefundItem entity."""

from sqlalchemy import DECIMAL, UUID, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class RefundItem(Base):
    __tablename__ = "refund_items"

    refund_item_id = Column(UUID, primary_key=True)
    refund_case_id = Column(UUID, ForeignKey("refund_cases.refund_id"), nullable=False)
    product_id = Column(UUID, nullable=False)
    product_name = Column(String(255), nullable=False)
    requested_quantity = Column(Integer, nullable=False)
    original_unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_refund_amount = Column(DECIMAL(10, 2), nullable=False)

    # refund_case = relationship("RefundCase", back_populates="refund_items")  # Disabled due to FK constraint issues
