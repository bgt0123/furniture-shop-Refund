"""External order service integration."""

import httpx
from typing import Optional, Dict, Any
from src.infrastructure.config.config import settings
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class OrderService:
    """Order service client for external order system."""

    def __init__(self):
        self.base_url = settings.order_api_base_url
        self._client = None

    @property
    def client(self):
        """Lazy client initialization."""
        if not self.base_url:
            return None
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self._client

    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order details from external service."""
        client = self.client
        if not client:
            logger.warning("Order API base URL not configured")
            return None

        try:
            response = await client.get(f"/orders/{order_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch order {order_id}: {e}")
            return None

    async def validate_order_for_refund(self, order_id: str) -> bool:
        """Validate if order is eligible for refund."""
        order = await self.get_order(order_id)
        if not order:
            return False

        # Basic validation logic
        return order.get("status") in ["delivered", "shipped"]


# Global order service instance
order_service = OrderService()
