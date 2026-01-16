# Feature Specification: Customer Support and Refund Microservice

**Feature Branch**: `1-support-refund`  
**Created**: January 16, 2026  
**Status**: Draft  
**Input**: User description: "Create a customer support and refund microservice for a web shop for designer furniture that references orders, products and deliveries from the shop. The service manages support cases and refund cases based on orders and their products. Customers can open and close support cases and request refunds for specific order items from an open support case. When a refund is requested, a refund case is created and linked to the support case. Customer support can approve and execute refund cases by triggering a payment refund or recording a settlement reference, but only within 14 days after the delivery date provided by the webshop. Refund cases must support partial refunds of individual products and quantities. The service provides overview pages for support cases and refund cases showing their current status, customer, related order and products, and full history."

## User Scenarios & Testing

### User Story 1 - Customer Initiates Support Case (Priority: P1)

A customer can open a support case for their furniture order when they have issues with delivery, product quality, or other concerns. This basic support workflow establishes the foundation for refund processing.

**Why this priority**: Core functionality that enables the entire support workflow - without this, customers cannot initiate contact or request refunds.

**Independent Test**: Can be fully tested by having customers create support cases linked to their orders and verify support case creation and basic status tracking.

**Acceptance Scenarios**:

1. **Given** a customer has a completed order, **When** they open a support case for that order, **Then** a support case is created with status "open" and linked to the order
2. **Given** an open support case, **When** a customer provides additional details or closes the case, **Then** the case status and history are updated accordingly

---

### User Story 2 - Customer Requests Refund via Support Case (Priority: P1)

A customer can request a refund for specific items within an open support case, enabling partial refunds by product and quantity. The system creates a refund case linked to the support case.

**Why this priority**: Core refund functionality that transforms support cases into actionable financial requests.

**Independent Test**: Can be fully tested by having customers request refunds for specific order items and verifying refund case creation with correct product/quantity mapping.

**Acceptance Scenarios**:

1. **Given** an open support case for an order, **When** a customer requests refund for 2 of 4 chairs purchased, **Then** a refund case is created with status "pending approval" showing partial refund request calculated using original purchase price
2. **Given** a refund case exists, **When** customer modifies the requested refund items or quantity, **Then** the refund case is updated with the new request details

---

### User Story 3 - Support Agent Reviews and Processes Refunds (Priority: P1)

Support agents can approve refund cases and execute refunds through payment systems or by recording settlement references, but only within the 14-day delivery window.

**Why this priority**: Core business functionality that completes the refund workflow and ensures compliance with refund policies.

**Independent Test**: Can be fully tested by having support agents process refund requests within valid timeframes and verify refund execution or settlement recording.

**Acceptance Scenarios**:

1. **Given** a refund case requested within 14 days of delivery (validated via webshop order system), **When** a support agent approves and executes the refund, **Then** the system triggers payment refund via gateway API and updates case status to "completed"
2. **Given** a refund case requested after 14 days of delivery, **When** a support agent attempts to approve, **Then** the system prevents approval and informs the agent about the time limit

---

### User Story 4 - Comprehensive Case Management Views (Priority: P2)

System provides overview pages showing all support and refund cases with their current status, customer details, related orders/products, and full history for tracking and analytics.

**Why this priority**: Important for operational visibility and customer service management, but can follow core case handling functionality.

**Independent Test**: Can be independently tested by verifying that overview pages display complete case information including status transitions and historical data.

**Acceptance Scenarios**:

1. **Given** multiple support and refund cases exist, **When** viewing the overview page, **Then** all cases are displayed with current status, customer information, order details, and complete history
2. **Given** a specific case with multiple status transitions, **When** viewing its history, **Then** all actions and state changes are displayed chronologically with timestamps

### Edge Cases

- What happens when a customer requests refund for more items than were ordered?
- How does system handle refund requests for products that were discounted or bundled?
- What occurs when delivery date information is missing or incomplete?
- How are refund cases handled when the original payment method is no longer available?
- Multiple refund cases can be created for the same support case to handle different product issues

## Requirements

### Functional Requirements

- **FR-001**: Customers MUST be able to create support cases linked to their orders
- **FR-002**: Support cases MUST track current status (open, in-progress, closed, etc.)
- **FR-003**: Customers MUST be able to request refunds for specific products and quantities from open support cases
- **FR-004**: System MUST create refund cases automatically when refund requests are submitted
- **FR-005**: Refund cases MUST be linked to the originating support case
- **FR-006**: Support agents MUST be able to approve refund cases within 14 days of delivery date
- **FR-007**: System MUST prevent refund approvals beyond the 14-day delivery window
- **FR-008**: Refund cases MUST support partial refunds by individual product and quantity
- **FR-009**: Support agents MUST be able to execute refunds through payment systems
- **FR-010**: Support agents MUST be able to record settlement references for completed refunds
- **FR-011**: System MUST provide overview pages showing support cases with status, customer, order, products
- **FR-012**: System MUST provide overview pages showing refund cases with status, customer, order, products
- **FR-013**: Both overview pages MUST display full history of case activities and status changes
- **FR-014**: Customers can modify refund requests until the refund case is approved by support agents
- **FR-015**: Support agents can approve refunds directly using a single-level approval workflow

### Key Entities

- **Support Case**: Customer help request linked to specific orders - tracks status, customer details, order reference, products involved
- **Refund Case**: Financial request created from support cases - tracks refund status, approved amount (based on original purchase price), products/quantities, delivery date validation (from webshop order system)
- **Order Reference**: External order data containing products purchased, customer information, delivery dates
- **Customer**: End-user who initiates support cases and receives refunds
- **Support Agent**: Internal user who manages and processes refund cases using payment gateway API integration

## Clarifications

### Session 2025-01-16

- Q: Refund amount calculation methodology → A: Use original purchase price per product
- Q: Data source for delivery dates → A: Webshop order system  
- Q: Refund execution method integration → A: Payment gateway API integration
- Q: Customer refund request modification policy → A: Allow until refund case approval
- Q: Multiple refund cases handling for same support case → A: Allow multiple distinct refund cases

## Success Criteria

### Measurable Outcomes

- **SC-001**: Customers can create support cases for their orders in under 2 minutes
- **SC-002**: Refund processing from request to completion completes within 48 business hours for eligible cases
- **SC-003**: 95% of valid refund requests within the 14-day window are successfully processed
- **SC-004**: Support agents can process refund requests with 100% accuracy in product/quantity matching
- **SC-005**: System prevents 100% of refund approvals outside the 14-day delivery window
- **SC-006**: Users can view complete case history and status information in under 5 seconds
- **SC-007**: Customer satisfaction with refund process increases by 40% measured through surveys