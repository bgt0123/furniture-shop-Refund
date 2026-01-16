"""Payment gateway integration."""

import httpx
from typing import Optional, Dict, Any
from src.infrastructure.config.config import settings
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class PaymentGateway:
    """Payment gateway client for refund processing."""

    def __init__(self):
        self.base_url = settings.payment_gateway_api_base_url
        self.api_key = settings.payment_gateway_api_key
        self._client = None

    @property
    def client(self):
        """Lazy client initialization."""
        if not self.base_url:
            return None
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self.api_key or 'placeholder'}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def initiate_refund(
        self, transaction_id: str, amount: float, currency: str = "USD"
    ) -> Optional[Dict[str, Any]]:
        """Initiate refund via payment gateway."""
        client = self.client
        if not client:
            logger.warning("Payment gateway API base URL not configured")
            return None

        if not self.api_key:
            logger.warning("Payment gateway API key not configured")
            return None

        payload = {
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
        }

        try:
            response = await client.post("/refunds", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to initiate refund: {e}")
            return None

    async def check_refund_status(self, refund_id: str) -> Optional[Dict[str, Any]]:
        """Check refund status."""
        client = self.client
        if not client:
            logger.warning("Payment gateway API base URL not configured")
            return None

        try:
            response = await client.get(f"/refunds/{refund_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to check refund status: {e}")
            return None


# Global payment gateway instance
payment_gateway = PaymentGateway()
