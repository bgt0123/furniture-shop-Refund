# Feature Specification: Support and Refund Service Workflow

**Feature Branch**: `001-support-refund-workflow`  
**Created**: January 17, 2026  
**Status**: Draft  
**Input**: User description: "We are building an online designer furniture shop using DDD and microservices, a Support Service and a Refund Service, both referencing orders, products, and deliveries from the shop. Customers can open a support case to ask questions or request a refund, optionally providing details and evidence, which is mandatory for a refund request. Refunds can be requested within 14 days after delivery, and may also be allowed if the product is damaged or defective. A support case may contain multiple refund requests. The counterpart role support agent can respond to the support case in general and, for each refund request, decide whether a refund is allowed (approved or rejected)."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Customer Submits Support Case and Refund Request (Priority: P1)

A customer discovers an issue with their furniture purchase and needs assistance or a refund. They create a support case, provide necessary details, and attach evidence when requesting a refund.

**Why this priority**: This is the foundational workflow that enables customers to initiate support interactions, providing immediate value by addressing their concerns.

**Independent Test**: Can be fully tested by allowing customers to create support cases with refund requests and documentation uploads, delivering immediate resolution pathways.

**Acceptance Scenarios**:

1. **Given** a customer has received a furniture delivery, **When** they create a support case with refund request and provide valid evidence, **Then** the system accepts the refund request for agent review
2. **Given** a customer wants to ask general questions, **When** they create a support case without refund request, **Then** the system creates a general support case for agent response

---

### User Story 2 - Support Agent Reviews and Decides on Refund Requests (Priority: P2)

A support agent evaluates refund requests within a support case, examining evidence and delivery dates to make approval/rejection decisions while providing general support responses.

**Why this priority**: This enables the business to process and resolve customer refund requests, ensuring compliance with policies while maintaining customer satisfaction.

**Independent Test**: Can be fully tested by allowing agents to view refund requests, assess evidence against policies, and make approval decisions independently.

**Acceptance Scenarios**:

1. **Given** an agent is reviewing a refund request within 14 days of delivery, **When** they approve the refund, **Then** the refund is processed according to policy
2. **Given** an agent is reviewing a refund request with product damage evidence, **When** they approve despite delivery timing, **Then** the refund proceeds based on defect criteria

---

### User Story 3 - Single Refund Request with Multiple Products Management (Priority: P3)

Each support case contains exactly one refund request, but that refund request can include multiple products from the order. The system prevents multiple refund requests for the same product.

**Why this priority**: This simplifies the customer experience while maintaining flexibility for refunding multiple items from the same order.

**Independent Test**: Can be fully tested by allowing customers to select multiple products for refund within a single refund request.

**Acceptance Scenarios**:

1. **Given** a support case for an order with multiple products, **When** a customer creates a refund request selecting specific products, **Then** the refund request includes only the selected products
2. **Given** a product has already been included in a refund request, **When** customer tries to create another refund request for the same product, **Then** the system prevents it

---

### User Story 4 - Shared Dashboard with Role-Based Access (Priority: P2)

Customers and support agents access the same web dashboard interface, but with different permissions and features tailored to their roles, providing a consistent user experience while maintaining security boundaries.

**Why this priority**: Provides unified interface experience while ensuring proper access control and workflow separation between customer self-service and agent administration.

**Independent Test**: Can be fully tested by verifying customer-only access to own cases and agent access to multiple customer cases with administrative controls.

**Acceptance Scenarios**:

1. **Given** a customer logs into the dashboard, **When** they access their support cases, **Then** they see only their own cases with create/message capabilities
2. **Given** a support agent logs into the dashboard, **When** they access support cases, **Then** they see assigned cases with decision-making capabilities across multiple customers

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- What happens when a refund request is submitted more than 14 days after delivery without damage evidence?
- How does system handle incomplete evidence submissions for refund requests?
- What occurs when agents need to request additional evidence before making decisions?
 // What happens when a customer wants to refund additional products after initial refund request? // How is partial product quantity refund handled?

### Functional Requirements

- **FR-001**: Customers MUST be able to create support cases for general questions or refund requests
- **FR-002**: Customers MUST provide details and photographic evidence when submitting refund requests
- **FR-003**: Refund requests MUST only be allowed within 14 days of delivery or for damaged/defective products
- **FR-004**: Each support case MUST contain exactly one refund request
- **FR-014**: A refund request MUST be able to include multiple products from the same order
- **FR-015**: The system MUST prevent multiple refund requests for the same product
- **FR-005**: Support agents MUST be able to respond to support cases with general messages
- **FR-006**: Support agents MUST be able to approve or reject each refund request individually
- **FR-007**: The system MUST reference orders and products from the shop servicere
- **FR-008**: Refund decisions MUST be recorded with timestamps and agent information
- **FR-009**: Approved refunds MUST be processed as full purchase price refunds with payment method options
- **FR-010**: The system MUST maintain separation between Support Service and Refund Service concerns, with RefundRequest fully managed by Refund Service
- **FR-011**: Customers MUST authenticate (via external Auth Service) before submitting support cases and refund requests
- **FR-012**: Support agents MUST authenticate (via external Auth Service) and have role-based access to assigned cases
- **FR-013**: The system MUST prevent customers from accessing other customers' support cases
- **FR-016**: Support cases MUST have defined state transitions: Open → In Progress → Closed
- **FR-017**: Support cases MUST have a case_type field (Question or Refund) to distinguish between types
- **FR-018**: RefundRequest MUST be created via Refund Service API when Support Case has type 'Refund'
- **FR-019**: The system MUST provide a shared dashboard interface for both customers and support agents
- **FR-020**: Dashboard MUST display different features and permissions based on user role (customer vs agent)
- **FR-021**: Customers MUST only see and manage their own support cases in the dashboard
- **FR-022**: Support agents MUST be able to view and process multiple customer cases in the dashboard
- **FR-023**: Dashboard MUST provide visual indicators for case status and workflow progress

### Key Entities *(include if feature involves data)*

- **SupportCase** (Support Service): Represents a customer inquiry containing general questions or refund request references
- **RefundRequest** (Refund Service): Single refund submission that can include multiple products from an order
- **SupportAgent**: User role responsible for reviewing cases and making refund decisions
- **Customer**: End-user initiating support interactions and requesting refunds

### Service Responsibilities

- **Support Service**: Manages SupportCase lifecycle including case_type, handles general support interactions
- **Refund Service**: Manages RefundRequest lifecycle, validates eligibility, processes refund decisions

**Authentication Note**: Login and authentication services are NOT part of these microservices. Authentication is handled by a separate Auth Service that provides user identity and role information. These services rely on authenticated session tokens or API keys for authorization checks.

### Dashboard Interface

**Shared Dashboard with Role-Based Access**: Customers and Support Agents will use the same web-based dashboard interface, with different permissions and available actions based on their roles. The dashboard integrates with an external Authentication Service for user identity and role management.

**Authentication Integration**:
- Dashboard communicates with external Auth Service for login and session management
- User roles (Customer/Agent) are provided by Auth Service
- Session tokens validate user identity and permissions
- No authentication logic implemented in Support or Refund Services

**Customer Dashboard Features**:
- View and manage own support cases
- Create new support cases (Question or Refund type)
- Submit refund evidence photos
- View support case status and history
- Communicate with support agents through message interface
- View refund decision results and status

**Support Agent Dashboard Features**:
- View assigned support cases in dashboard queue
- Process both question-type and refund-type cases
- Review refund evidence and eligibility
- Make refund decisions (Approve/Reject/RequestMoreInfo)
- Submit support responses and internal notes
- Access case history across all customers (read-only)
- Close support cases after resolution
- Manage case assignments and workflow

**Role-Based Permissions**:
- **Customers**: Can only access their own cases, create new cases, and respond to assigned agents
- **Agents**: Can access multiple customer cases, make decisions, and perform administrative actions
- **Authentication**: External Auth Service provides role-based access control
- **Audit Trail**: All actions are logged with user role and timestamp for security

## Clarifications

### Session 2026-01-17

- Q: Should there be role-based access control for support agents vs customers? → A: Customer self-service with agent approval workflow
- Q: How should refund requests relate to support cases and orders? → A: Each SupportCase can have only one RefundRequest covering the entire order
- Q: How should refund amounts be determined for approved requests? → A: Full purchase price refund, options: money, voucher, or replacement
- Q: What types of evidence should be acceptable for refund requests? → A: Only Photos
- Q: Should there be automatic notifications for case status changes? → A: No
- Q: Should support cases have defined states? → A: Open → In Progress → Closed

### Service Boundary Clarification

- RefundRequest is part of the Refund Service domain and managed entirely by Refund Service
- Support Case Service creates SupportCase entities and, when case_type='Refund', calls Refund Service API to create RefundRequest
- SupportCase references RefundRequest via refund_request_id field
- Service communication happens via API calls between Support Service and Refund Service

### Workflow

```
Customer creates SupportCase
     ↓
Support Service validates case_type ('Question' or 'Refund')
     ↓
If case_type='Refund':
    Support Service → Refund Service API: CreateRefundRequest
    Refund Service validates refund eligibility
    Refund Service returns refund_request_id
    Support Service updates SupportCase.refund_request_id
     ↓
Agent reviews SupportCase and RefundRequest separately
Refund decisions made in Refund Service
Support responses handled in Support Service
```

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Customers can submit support cases with refund requests in under 5 minutes
- **SC-002**: Support agents process refund requests within 24 hours of submission
- **SC-003**: 95% of eligible refund requests are correctly identified and processed
- **SC-004**: Customers successfully submit required evidence with 90% of refund requests
- **SC-005**: Support case resolution reduces customer follow-up inquiries by 60%
