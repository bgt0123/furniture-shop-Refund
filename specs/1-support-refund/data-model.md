# Data Model: Customer Support and Refund Microservice

**Date**: January 16, 2026
**Source**: Feature specification analysis

## Core Entities

### SupportCase (Aggregate Root)
**Description**: Customer support request linked to specific orders
**Fields**:
- `case_id` (UUID, Primary Key)
- `customer_id` (UUID, Foreign Key)
- `order_id` (UUID, Foreign Key to external order system)
- `title` (String, Required)
- `description` (Text, Optional)
- `status` (Enum: open, in-progress, resolved, closed)
- `created_at` (DateTime, Auto-generated)
- `updated_at` (DateTime, Auto-updated)
- `closed_at` (DateTime, Optional)

**Relationships**:
- One-to-Many with RefundCase
- Many-to-One with Customer

### RefundCase (Aggregate Root)
**Description**: Financial refund request created from a support case
**Fields**:
- `refund_id` (UUID, Primary Key)
- `support_case_id` (UUID, Foreign Key)
- `status` (Enum: pending, approved, executed, failed, cancelled)
- `requested_amount` (Decimal, Calculated from products)
- `approved_amount` (Decimal, Amount approved by support agent)
- `delivery_date` (Date, From order system)
- `refund_requested_at` (DateTime)
- `refund_approved_at` (DateTime, Optional)
- `refund_executed_at` (DateTime, Optional)
- `settlement_reference` (String, Optional)
- `failure_reason` (String, Optional)

**Relationships**:
- Many-to-One with SupportCase
- One-to-Many with RefundItem

### RefundItem (Value Object)
**Description**: Individual product item requested for refund
**Fields**:
- `refund_item_id` (UUID, Primary Key)
- `refund_case_id` (UUID, Foreign Key)
- `product_id` (UUID, From order system)
- `product_name` (String, For display purposes)
- `requested_quantity` (Integer)
- `original_unit_price` (Decimal)
- `total_refund_amount` (Decimal, Calculated)

**Relationships**:
- Many-to-One with RefundCase

### Customer (Entity)
**Description**: End-user who initiates support cases
**Fields**:
- `customer_id` (UUID, Primary Key)
- `email` (String, Required)
- `first_name` (String)
- `last_name` (String)
- `created_at` (DateTime)

**Relationships**:
- One-to-Many with SupportCase

### SupportAgent (Entity)
**Description**: Internal user who processes refund cases
**Fields**:
- `agent_id` (UUID, Primary Key)
- `email` (String, Required)
- `first_name` (String)
- `last_name` (String)
- `role` (Enum: agent, admin)
- `created_at` (DateTime)

**Relationships**:
- One-to-Many with RefundCase (via approved_by)

### OrderReference (External Entity Reference)
**Description**: External order data from webshop system
**Fields**:
- `order_id` (UUID, Primary Key, External)
- `customer_id` (UUID, External)
- `order_date` (DateTime)
- `delivery_date` (DateTime, Critical for 14-day validation)
- `total_amount` (Decimal)
- `status` (String)

## Value Objects

### Money (Value Object)
**Description**: Monetary value handling
- `amount` (Decimal)
- `currency` (String, Fixed to shop currency)

### CaseStatus (Enum)
- `open`, `in_progress`, `resolved`, `closed`

### RefundStatus (Enum)
- `pending`, `approved`, `executed`, `failed`, `cancelled`

## Aggregate Boundaries

### SupportCase Aggregate
**Root**: SupportCase
**Entities within aggregate**: RefundCase entities (via composition)
**Invariants**:
- Support case can have multiple refund cases
- Support case status transitions follow lifecycle: open → in-progress → resolved → closed
- Refund cases can only be created for open support cases

### RefundCase Aggregate
**Root**: RefundCase
**Entities within aggregate**: RefundItem entities
**Invariants**:
- Refund amount must be calculated from original purchase prices
- Refund approval only possible within 14 days of delivery date
- Partial refund requests require specific product and quantity selection
- Refund execution must include settlement reference or payment gateway response

## Database Schema Design

### Core Tables

#### support_cases
```sql
CREATE TABLE support_cases (
    case_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    order_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('open', 'in-progress', 'resolved', 'closed') NOT NULL DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL
);
```

#### refund_cases
```sql
CREATE TABLE refund_cases (
    refund_id UUID PRIMARY KEY,
    support_case_id UUID NOT NULL,
    status ENUM('pending', 'approved', 'executed', 'failed', 'cancelled') NOT NULL DEFAULT 'pending',
    requested_amount DECIMAL(10,2) NOT NULL,
    approved_amount DECIMAL(10,2),
    delivery_date DATE NOT NULL,
    refund_requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    refund_approved_at TIMESTAMP NULL,
    refund_executed_at TIMESTAMP NULL,
    settlement_reference VARCHAR(255),
    failure_reason TEXT,
    approved_by UUID,
    FOREIGN KEY (support_case_id) REFERENCES support_cases(case_id)
);
```

#### refund_items
```sql
CREATE TABLE refund_items (
    refund_item_id UUID PRIMARY KEY,
    refund_case_id UUID NOT NULL,
    product_id UUID NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    requested_quantity INTEGER NOT NULL,
    original_unit_price DECIMAL(10,2) NOT NULL,
    total_refund_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (refund_case_id) REFERENCES refund_cases(refund_id)
);
```

### Indexing Strategy

**Performance-Critical Indexes**:
- `support_cases(customer_id, status)` - Quick customer case lookup
- `support_cases(order_id)` - Order-based case lookup
- `refund_cases(support_case_id)` - Quick refund case lookup by support case
- `refund_cases(status, delivery_date)` - Refund approval eligibility checking
- `refund_cases(customer_id, status)` - Customer refund overview

## Business Rules and Constraints

### Domain Rules

#### Support Case Rules
- Case can only be created for existing orders
- Only customer who placed order can create support case
- Case status transitions must follow defined lifecycle
- Closed cases cannot have new refund requests

#### Refund Case Rules
- Refund request must be within open support case
- Refund approval requires delivery date validation (≤14 days)
- Requested amount calculated from original purchase price
- Partial refunds require specific product and quantity
- Once approved, modification requires approval reset

#### Refund Execution Rules
- Must record settlement reference or payment gateway transaction ID
- Failed executions require rollback and user notification
- Execution must be idempotent to prevent duplicate refunds

### Validation Rules

#### Amount Validation
- Requested amount cannot exceed order total
- Approved amount cannot exceed requested amount
- Unit prices must match original purchase prices

#### Temporal Validation
- Delivery date must be validated against order system
- 14-day window calculated from delivery date
- Timezone handling for accurate window calculation

## Relationship Diagram

```
Customer (1) ──────── (N) SupportCase (1) ──────── (N) RefundCase (1) ──────── (N) RefundItem
                    │
                    └─────── OrderReference (external)
```

## External Dependencies

### Order System Integration
- Delivery date validation
- Product and pricing information
- Order status verification

### Payment Gateway Integration
- Refund execution
- Settlement reference generation
- Error handling and rollback