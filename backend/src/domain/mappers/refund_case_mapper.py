"""Mapper for converting between RefundCase SQLAlchemy entity and domain aggregates."""

from src.domain.aggregates.refund_case_aggregate import RefundCaseAggregate
from src.domain.entities.refund_case import RefundCase as RefundCaseEntity
from src.domain.value_objects.refund_status import RefundStatus
from src.domain.entities.refund_item import RefundItem as RefundItemEntity


class RefundCaseMapper:
    """Mapper for RefundCase conversions."""

    @staticmethod
    def to_aggregate(entity: RefundCaseEntity) -> RefundCaseAggregate:
        """Convert SQLAlchemy entity to domain aggregate."""
        if not entity:
            return None

        # Extract values from entity (handling SQLAlchemy Column types)
        refund_id = str(entity.refund_id) if entity.refund_id else None
        support_case_id = (
            str(entity.support_case_id) if entity.support_case_id else None
        )
        delivery_date = entity.delivery_date
        refund_requested_at = entity.refund_requested_at
        status = RefundStatus(entity.status) if entity.status else RefundStatus.PENDING
        requested_amount = (
            float(entity.requested_amount) if entity.requested_amount else 0.0
        )
        approved_amount = (
            float(entity.approved_amount) if entity.approved_amount else None
        )
        refund_approved_at = entity.refund_approved_at
        refund_executed_at = entity.refund_executed_at
        settlement_reference = entity.settlement_reference
        failure_reason = entity.failure_reason
        approved_by = str(entity.approved_by) if entity.approved_by else None

        # Map refund items (simplified for now)
        refund_items = []
        if entity.refund_items:
            for item in entity.refund_items:
                refund_items.append(item)  # Simple mapping

        return RefundCaseAggregate(
            refund_id=refund_id,
            support_case_id=support_case_id,
            refund_items=refund_items,
            delivery_date=delivery_date,
            refund_requested_at=refund_requested_at,
            status=status,
            requested_amount=requested_amount,
            approved_amount=approved_amount,
            refund_approved_at=refund_approved_at,
            refund_executed_at=refund_executed_at,
            settlement_reference=settlement_reference,
            failure_reason=failure_reason,
            approved_by=approved_by,
        )

    @staticmethod
    def to_entity(aggregate: RefundCaseAggregate) -> RefundCaseEntity:
        """Convert domain aggregate to SQLAlchemy entity."""
        if not aggregate:
            return None

        entity = RefundCaseEntity()
        entity.refund_id = aggregate.refund_id
        entity.support_case_id = aggregate.support_case_id
        entity.delivery_date = aggregate.delivery_date
        entity.refund_requested_at = aggregate.refund_requested_at
        entity.status = aggregate.status.value
        entity.requested_amount = (
            str(aggregate.requested_amount) if aggregate.requested_amount else None
        )
        entity.approved_amount = (
            str(aggregate.approved_amount) if aggregate.approved_amount else None
        )
        entity.refund_approved_at = aggregate.refund_approved_at
        entity.refund_executed_at = aggregate.refund_executed_at
        entity.settlement_reference = aggregate.settlement_reference
        entity.failure_reason = aggregate.failure_reason
        entity.approved_by = aggregate.approved_by

        return entity
