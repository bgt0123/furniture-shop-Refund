"""Refund execution service for processing approved refunds."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.aggregates.refund_case_aggregate import RefundCaseAggregate
from src.domain.entities.support_agent import SupportAgent
from src.domain.value_objects.refund_status import RefundStatus
from src.domain.repositories.refund_case_repository import RefundCaseRepository
from src.infrastructure.external.payment_gateway import PaymentGateway


class RefundExecutionService:
    """Service for executing approved refunds through payment gateway."""

    def __init__(
        self, repository: RefundCaseRepository, payment_gateway: PaymentGateway
    ):
        """Initialize with repository and payment gateway.

        Args:
            repository: Repository for refund case operations
            payment_gateway: Payment gateway integration service
        """
        self.repository = repository
        self.payment_gateway = payment_gateway

    async def execute_refund(
        self,
        refund_case: RefundCaseAggregate,
        agent: SupportAgent,
        settlement_reference: Optional[str] = None,
    ) -> RefundCaseAggregate:
        """Execute an approved refund through payment gateway.

        Args:
            refund_case: The refund case to execute
            agent: The support agent executing the refund
            settlement_reference: Optional settlement reference

        Returns:
            Updated refund case with execution details

        Raises:
            ValueError: If refund case is not in approved status
        """
        # Validate refund case is in approved status
        if refund_case.status != RefundStatus.APPROVED:
            raise ValueError(
                f"Cannot execute refund case in {refund_case.status} status"
            )

        try:
            # Execute refund through payment gateway
            if settlement_reference:
                # Use refund with settlement reference - use transaction ID as the refund_id
                transaction_id = settlement_reference
                result = await self.payment_gateway.initiate_refund(
                    transaction_id, float(refund_case.approved_amount)
                )
            else:
                # Execute refund using the refund case ID as transaction ID
                result = await self.payment_gateway.initiate_refund(
                    str(refund_case.refund_id), float(refund_case.approved_amount)
                )

            # Update refund case with execution details
            if result and result.get("success"):
                refund_case.execute_refund(
                    result.get("transaction_id") or settlement_reference
                )
            else:
                refund_case.mark_refund_as_failed("Payment gateway execution failed")

        except Exception as e:
            # Handle payment gateway failures
            refund_case.mark_refund_as_failed(str(e))

        # Convert aggregate back to entity and save
        entity = self._aggregate_to_entity(refund_case)
        saved_entity = await self.repository.save(entity)

        # Convert back to aggregate
        return self._entity_to_aggregate(saved_entity)

    async def retry_failed_refund(
        self, refund_case: RefundCaseAggregate, agent: SupportAgent
    ) -> RefundCaseAggregate:
        """Retry a failed refund execution.

        Args:
            refund_case: The failed refund case to retry
            agent: The support agent retrying the refund

        Returns:
            Updated refund case with retry details

        Raises:
            ValueError: If refund case is not in failed status
        """
        # Validate refund case is in failed status
        if refund_case.status != RefundStatus.FAILED:
            raise ValueError(f"Cannot retry refund case in {refund_case.status} status")

        # Reset status to approved for retry
        refund_case.status = RefundStatus.APPROVED
        refund_case.failure_reason = None

        # Convert aggregate back to entity and save
        entity = self._aggregate_to_entity(refund_case)
        saved_entity = await self.repository.save(entity)

        # Convert back to aggregate
        return self._entity_to_aggregate(saved_entity)

    def get_executed_refunds_for_agent(
        self, agent: SupportAgent
    ) -> list[RefundCaseAggregate]:
        """Get all executed refunds processed by a support agent.

        Args:
            agent: The support agent

        Returns:
            List of executed refund cases
        """
        entities = self.repository.find_by_status_and_approver(
            "executed", agent.agent_id
        )
        return [self._entity_to_aggregate(entity) for entity in entities]

    def _aggregate_to_entity(self, aggregate: RefundCaseAggregate):
        """Convert aggregate to SQLAlchemy entity."""
        # This is a placeholder - actual implementation would map fields
        from src.domain.entities.refund_case import RefundCase

        return RefundCase()

    def _entity_to_aggregate(self, entity) -> RefundCaseAggregate:
        """Convert SQLAlchemy entity to aggregate."""
        # This is a placeholder - actual implementation would map fields
        return RefundCaseAggregate(
            refund_id=entity.refund_id,
            support_case_id=entity.support_case_id,
            refund_items=[],  # TODO: Map actual refund items
            delivery_date=entity.delivery_date,
            refund_requested_at=entity.refund_requested_at,
            status=RefundStatus(entity.status),
            requested_amount=float(entity.requested_amount)
            if entity.requested_amount
            else None,
            approved_amount=float(entity.approved_amount)
            if entity.approved_amount
            else None,
            refund_approved_at=entity.refund_approved_at,
            refund_executed_at=entity.refund_executed_at,
            settlement_reference=entity.settlement_reference,
            failure_reason=entity.failure_reason,
            approved_by=entity.approved_by,
        )
