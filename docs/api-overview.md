# API Documentation - Support and Refund Services

## Overview

This document provides comprehensive API documentation for the Furniture Shop Support and Refund Services microservices architecture.

## Service Endpoints

### Support Service (Port 8001)

#### Support Cases API
- **Create Support Case**: `POST /support-cases/`
- **Get All Cases**: `GET /support-cases/`
- **Get Case by ID**: `GET /support-cases/{case_number}`
- **Update Case**: `PUT /support-cases/{case_number}`
- **Close Case**: `POST /support-cases/{case_number}/close`

#### Support Case Responses API
- **Add Response**: `POST /support-cases/{case_number}/responses`
- **Get Responses**: `GET /support-cases/{case_number}/responses`

### Refund Service (Port 8002)

#### Refund Cases API
- **Create Refund Request**: `POST /refund-cases/`
- **Get All Refund Cases**: `GET /refund-cases/`
- **Get Case by ID**: `GET /refund-cases/{refund_case_id}`
- **Get Detailed Case**: `GET /refund-cases/{refund_case_id}/detailed`
- **Get Customer's Cases**: `GET /refund-cases/customer/{customer_id}`

#### Refund Decision & Evidence API
- **Make Refund Decision**: `POST /refund-cases/{refund_case_id}/decisions`
- **Get Evidence**: `GET /refund-cases/{refund_case_id}/evidence`
- **Get Responses**: `GET /refund-cases/{refund_case_id}/responses`

## Authentication Requirements

- All endpoints require authenticated user context
- Role-based access control:
  - **Customers**: Can only access their own cases
  - **Agents**: Can access all cases
  - **Administrators**: Full system access

## Data Models

### Support Case
```json
{
  "case_number": "SC-18205F38",
  "customer_id": "cust-123",
  "case_type": "Refund",
  "subject": "Defective product",
  "description": "Detailed description of the issue",
  "status": "Open",
  "refund_request_ids": ["RR-AB54A839"],
  "assigned_agent_id": "agent-001",
  "order_id": "ORD-12345",
  "product_ids": ["FURN-001", "FURN-002"],
  "delivery_date": "2026-01-20",
  "comments": [
    {
      "comment_id": "COM-001",
      "author_id": "cust-123",
      "author_type": "customer",
      "content": "Initial issue report"
    }
  ],
  "case_history": [],
  "created_at": "2026-01-21T14:36:31.769374",
  "updated_at": "2026-01-21T14:36:31.769374"
}
```

### Refund Request
```json
{
  "refund_case_id": "RR-AB54A839",
  "case_number": "SC-18205F38",
  "customer_id": "cust-123",
  "order_id": "ORD-12345",
  "product_ids": ["FURN-001", "FURN-002"],
  "status": "pending",
  "request_reason": "Product arrived damaged",
  "evidence_photos": ["damage_photo1.jpg"],
  "decision_reason": "Refund approved due to product defect",
  "refund_amount": {"amount": 199.99, "currency": "USD"},
  "decision_date": "2026-01-21T16:58:10.892",
  "decision_agent_id": "agent-001",
  "created_at": "2026-01-21T14:36:31.769374"
}
```

## Error Handling

### Common Error Responses

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "status_code": 400
}
```

### Status Codes
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

- Support Service: 100 requests/minute per IP
- Refund Service: 60 requests/minute per IP

## Versioning

Current API Version: **v1**

## Recent Changes

### Service Health (January 2026)
- **Refund Service**: Fixed startup errors related to database schema imports
- **Both Services**: Enhanced database initialization with proper table creation
- **Data Models**: Updated to reflect actual API structure
- **Endpoints**: Added comprehensive endpoint listing based on current implementation

### Key Fixes
- Removed obsolete `CREATE_CASE_TIMELINE_TABLE` import from refund service
- Fixed SQL query using `support_case_number` column instead of `refund_case_id`
- Improved database initialization with table drops to ensure clean schema creation

## Testing

See `quickstart.md` for testing instructions and development setup.