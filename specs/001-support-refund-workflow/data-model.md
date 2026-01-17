# Data Model: Support and Refund Service

## Overview
This document defines the entities, aggregates, and relationships for the Support and Refund Service implementation.

## Aggregate Roots

### SupportCase (Aggregate Root)
**Purpose**: Represents a customer inquiry that may contain refund requests

**Attributes**:
- case_number: String (business identifier, e.g., "SC-2026-001")
- customer_id: String (reference to shop customer)
- case_type: Enum (Question, Refund) - indicates if case contains refund request
- refund_request_id: String (nullable, reference to RefundService when case_type="Refund")
- subject: String
- description: String
- status: Enum (Open, In Progress, Closed)
- created_at: DateTime
- updated_at: DateTime
- assigned_agent_id: String (nullable)

**Rules**:
- Customers can only access their own support cases
- Status transitions must follow: Open → In Progress → Closed
- Only one refund request allowed per support case

### RefundRequest (Entity)
**Purpose**: Single refund request managed by Refund Service domain with separate database

**Attributes**:
- refund_request_id: String (business identifier, e.g., "RR-2026-001")
- case_number: String (business reference to SupportCase in Support Service)
- product_ids: List[String] (products from order to refund)
- request_reason: String
- evidence_photos: List[String] (file references)
- status: Enum (Pending, Approved, Rejected)
- decision_reason: String (nullable)
- decision_date: DateTime (nullable)
- decision_agent_id: String (nullable)

**Rules**:
- Must include at least one product
- Evidence photos must be provided
- Cannot refund same product multiple times
- Decision requires assigned agent
- Case reference (case_number) must resolve to valid SupportCase in Support Service

## Value Objects

### Money
**Purpose**: Represents monetary values consistently

**Attributes**:
- amount: Decimal
- currency: String (e.g., "EUR")

### CaseTimeline
**Purpose**: Track status changes and updates

**Attributes**:
- timestamp: DateTime
- status: String
- actor: String
- notes: String

## Domain Services

### EligibilityService
**Purpose**: Validate refund eligibility against business rules

**Rules**:
- Must be within 14 days of delivery OR product defective
- Products must exist in referenced order
- Cannot process already refunded products

### RefundCalculationService  
**Purpose**: Calculate refund amounts based on products

**Rules**:
- Full purchase price for eligible products
- Support money, voucher, or replacement delivery options

## Relationships (Cross-Service)

```
SupportService (support.db)           RefundService (refund.db)
      │                                      │
      ├── SupportCase (references          ├── RefundRequest 
      │   refund_request_id)              │   (has case_number reference)
      │                                    └── Agent
      └── Customer ──→ ShopService 
```

**Note**: Relationships between services are maintained via cross-service API calls and business identifiers (case_number) rather than database foreign keys. SupportCase references RefundRequest by refund_request_id (optional depending on case type).

## External References

**Shop Service Integration**:
- Order details (real-time lookup)
- Product information (real-time lookup) 
- Customer profile (reference only)

Note: Delivery information NOT referenced as per clarification decision