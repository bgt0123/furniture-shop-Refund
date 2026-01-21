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

#### Responses API
- **Add Response**: `POST /support-cases/{case_number}/responses`
- **Get Responses**: `GET /support-cases/{case_number}/responses`

### Refund Service (Port 8002)

#### Refund Cases API
- **Create Refund Request**: `POST /refund-cases/`
- **Get All Refund Cases**: `GET /refund-cases/`
- **Get Refund Case Details**: `GET /refund-cases/{refund_case_id}`
- **Get Customer's Refund Cases**: `GET /refund-cases/customer/{customer_id}`

#### Refund Decisions API
- **Make Refund Decision**: `POST /refund-cases/{refund_case_id}/decisions`
- **Get Decision Evidence**: `GET /refund-cases/{refund_case_id}/evidence`

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
  "subject": "Defective product",
  "description": "Detailed description of the issue",
  "case_type": "Refund",
  "status": "Open",
  "refund_request_id": "RR-AB54A839",
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
  "decision_reason": "Refund approved due to product defect",
  "decision_date": "2026-01-21T16:58:10.892",
  "decision_agent_id": "agent-001"
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

## Testing

See `quickstart.md` for testing instructions and development setup.