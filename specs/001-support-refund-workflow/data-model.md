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
- support_responses: List[SupportResponse] (message history)
- status: Enum (Open, In Progress, Closed)
- created_at: DateTime
- updated_at: DateTime
- assigned_agent_id: String (nullable)

**Rules**:
- Customers can only access their own support cases
- Status transitions must follow: Open → In Progress → Closed
- Only one refund request allowed per support case

### SupportResponse (Entity)
**Purpose**: Individual response message within a support case

**Attributes**:
- response_id: String (business identifier)
- case_number: String (reference to SupportCase)
- sender_id: String (customer_id or agent_id)
- sender_type: Enum (Customer, Agent)
- content: String (response text)
- attachments: List[String] (file references)
- timestamp: DateTime
- is_internal: Boolean (notes not visible to customer)
- message_type: Enum (Question, Answer, StatusUpdate, CloseCase)

**Rules**:
- Responses must be linked to valid support cases
- Agents can create internal notes not visible to customers
- Customer responses require customer authentication
- Closing cases requires agent authorization

### RefundCase (Aggregate Root)
**Purpose**: Represents the complete refund workflow and state management for the Refund Service domain

**Attributes**:
- refund_case_id: String (business identifier, e.g., "RC-2026-001")
- case_number: String (business reference to SupportCase in Support Service)
- customer_id: String (reference to shop customer)
- order_id: String (reference to shop order)
- refund_request: RefundRequest (entity - see below)
- refund_responses: List[RefundResponse] (decision responses)
- timeline: List[CaseTimeline] (audit trail of status changes)
- created_at: DateTime
- updated_at: DateTime

**Rules**:
- Contains one RefundRequest entity
- Contains multiple RefundResponse entities (decision history)
- Manages refund decision lifecycle (Pending → Approved/Rejected)
- Maintains audit trail of all status changes
- Validates refund eligibility and business rules
- Coordinates refund processing workflow

### RefundRequest (Entity)
**Purpose**: Single refund request managed by Refund Service domain

**Attributes**:
- refund_request_id: String (business identifier, e.g., "RR-2026-001")
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

### RefundResponse (Entity)
**Purpose**: Formal response to a refund request decision

**Attributes**:
- response_id: String (business identifier)
- refund_request_id: String (reference to RefundRequest)
- agent_id: String (support agent who responded)
- response_type: Enum (Approval, Rejection, RequestAdditionalEvidence)
- response_content: String (detailed explanation)
- attachments: List[String] (file references for documentation)
- timestamp: DateTime
- refund_amount: Money (nullable, for approved refunds)
- refund_method: Enum (Money, Voucher, Replacement)

**Rules**:
- Responses must be linked to valid refund requests
- Approved responses must specify refund amount and method
- Rejection responses must provide clear reasoning

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

### ResponseContent
**Purpose**: Structured content for support and refund responses

**Attributes**:
- title: String (optional)
- body: String (required)
- action_items: List[String] (specific steps or requests)
- next_steps: String (guidance for customer)
- resolution_type: Enum (Information, ActionRequired, Closed)

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
      ├── SupportCase (aggregate root)      ├── RefundCase (aggregate root)
      │   ├── SupportResponse (entity)     │   ├── RefundRequest (entity)
      │   └── Customer                    │   ├── RefundResponse (entity)
      │                                    │   └── Agent
      ├── Agent                             │
      └── Customer ──→ ShopService 
```

**Note**: Relationships between services are maintained via cross-service API calls and business identifiers (case_number) rather than database foreign keys. SupportCase references RefundService via refund_case_id (optional depending on case type). The RefundCase aggregate coordinates the entire refund workflow.

## External References

**Shop Service Integration**:
- Order details (real-time lookup)
- Product information (real-time lookup) 
- Customer profile (reference only)

## Authentication Architecture

**External Authentication Service**: Authentication is handled by a separate Auth Service. These microservices rely on authenticated user identities and roles provided by the Auth Service.

**Integration Points**:
- Support and Refund Services accept authenticated user IDs and roles from Auth Service
- No password management or login logic implemented
- User validation occurs at API gateway or service mesh level
- All actions are logged with authenticated user identity

Note: Delivery information NOT referenced as per clarification decision