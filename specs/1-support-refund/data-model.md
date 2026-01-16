# Data Model: Customer Support and Refund Microservice

## Core Entities

### Support Case
**Description**: Customer help request linked to specific orders

**Attributes**:
- `id` (UUID, primary key)
- `customer_id` (UUID, foreign key)
- `order_reference` (string, external order ID)
- `subject` (string)
- `description` (text)
- `status` (enum: OPEN, IN_PROGRESS, CLOSED, ESCALATED)
- `priority` (enum: LOW, MEDIUM, HIGH, URGENT)
- `created_at` (datetime)
- `updated_at` (datetime)
- `closed_at` (datetime, nullable)

**Relationships**:
- One Support Case → Many Refund Cases (optional)
- One Customer → Many Support Cases

### Refund Case
**Description**: Financial request created from support cases

**Attributes**:
- `id` (UUID, primary key)
- `support_case_id` (UUID, foreign key)
- `customer_id` (UUID, foreign key)
- `order_reference` (string, external order ID)
- `delivery_date` (date, from order system)
- `refund_amount` (decimal, calculated from products)
- `status` (enum: PENDING_APPROVAL, APPROVED, PROCESSING, COMPLETED, REJECTED)
- `approved_at` (datetime, nullable)
- `processed_at` (datetime, nullable)
- `approval_window_expires` (calculated field)
- `settlement_reference` (string, nullable)

**Relationships**:
- One Support Case → Many Refund Cases
- One Refund Case → Many Refund Line Items

### Refund Line Item
**Description**: Individual product refund request within a refund case

**Attributes**:
- `id` (UUID, primary key)
- `refund_case_id` (UUID, foreign key)
- `product_id` (string, external product ID)
- `product_name` (string)
- `original_price` (decimal)
- `requested_quantity` (integer)
- `approved_quantity` (integer, nullable)
- `approved_price` (decimal, nullable)

## Value Objects

### Monetary Amount
- `amount` (decimal)
- `currency` (ISO 4217 code, default EUR)

### Delivery Window Validation
- `delivery_date` (date)
- `current_date` (date)
- `days_since_delivery` (calculated)
- `is_within_window` (boolean, 14-day limit)

### Customer Information (from external system)
- `customer_id` (UUID)
- `email` (string)
- `name` (string)
- `contact_details` (JSON)

## Aggregates

### Support Case Aggregate
**Root**: Support Case
**Entities**: Refund Case, Refund Line Item
**Invariants**:
- Refund cases can only be created for open support cases
- Support case status transitions follow business workflow
- Refund cases require valid delivery date from order system

## Domain Services

### Refund Eligibility Service
- Validates delivery date window compliance
- Calculates maximum refundable amount
- Ensures product/quantity consistency

### Payment Processing Service  
- Executes refunds via payment gateway
- Records settlement references
- Handles partial and full refunds

## Database Schema Considerations

### Indexes
- `idx_support_case_customer` on SupportCase(customer_id)
- `idx_support_case_order` on SupportCase(order_reference)
- `idx_refund_case_support` on RefundCase(support_case_id)
- `idx_refund_case_status` on RefundCase(status)
- `idx_refund_case_delivery` on RefundCase(delivery_date)

### Constraints
- Status transitions enforced via check constraints
- Delivery date validation business rules
- Currency consistency across monetary fields