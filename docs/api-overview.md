# Furniture Shop API Overview

This document provides an overview of the backend API services for the Furniture Shop application.

## Service Architecture

### Microservices
- **Support Service** (`localhost:8001`) - Manages customer support cases and interactions
- **Refund Service** (`localhost:8002`) - Handles refund requests and refund processing

### Technology Stack
- **Backend**: FastAPI (Python 3.12+)
- **Frontend**: React 18
- **Database**: SQLite
- **Caching**: Redis

## API Endpoints

### Support Service (`localhost:8001`)

#### Support Cases Management
- **POST** `/support-cases/` - Create a new support case
- **GET** `/support-cases/` - Get all support cases (for agents)
- **GET** `/support-cases/{case_number}` - Get a support case by ID
- **GET** `/support-cases/customer/{customer_id}` - Get all support cases for a customer
- **PUT** `/support-cases/{case_number}` - Update a support case
- **PUT** `/support-cases/{case_number}/update-type` - Update case type
- **PUT** `/support-cases/{case_number}/close` - Close a support case

#### Comments & Interactions
- **POST** `/support-cases/{case_number}/comments` - Add a comment to a support case

#### Health & Status
- **GET** `/` - Service status
- **GET** `/health` - Health check

### Refund Service (`localhost:8002`)

#### Refund Request Management
- **POST** `/refund-cases/` - Create a new refund request
- **GET** `/refund-cases/` - Get all refund cases (for agents)
- **GET** `/refund-cases/{refund_case_id}` - Get basic refund case information
- **GET** `/refund-cases/{refund_case_id}/detailed` - Get detailed refund case information
- **GET** `/refund-cases/customer/{customer_id}` - Get customer's refund cases

#### Refund Processing
- **POST** `/refund-cases/{refund_case_id}/decisions` - Make refund decision (approve/reject)
- **GET** `/refund-cases/{refund_case_id}/responses` - Get refund responses/decisions

#### Service Information
- **GET** `/refund-cases/info` - API information
- **GET** `/` - Service status
- **GET** `/health` - Health check

## Data Models

### Support Case
```json
{
  "case_number": "string",
  "customer_id": "string",
  "case_type": "question|refund",
  "subject": "string",
  "description": "string",
  "status": "string",
  "refund_request_ids": ["string"],
  "assigned_agent_id": "string",
  "order_id": "string",
  "product_ids": ["string"],
  "delivery_date": "string (ISO)",
  "comments": ["Comment"],
  "case_history": ["CaseEvent"],
  "created_at": "string (ISO)",
  "updated_at": "string (ISO)"
}
```

### Refund
```json
{
  "refund_case_id": "string",
  "case_number": "string",
  "customer_id": "string",
  "order_id": "string",
  "status": "pending|approved|rejected",
  "created_at": "string (ISO)",
  "updated_at": "string (ISO)",
  "request_reason": "string",
  "product_ids": ["string"],
  "evidence_photos": ["string"],
  "support_case_details": {} // Optional
}
```

### Comment
```json
{
  "comment_id": "string",
  "case_number": "string",
  "author_id": "string",
  "author_type": "customer|agent|refund_service",
  "content": "string",
  "comment_type": "customer_comment|agent_response|refund_feedback",
  "attachments": ["string"],
  "timestamp": "string (ISO)",
  "is_internal": boolean
}
```

## Service Interaction Flow

### Create Support Case -> Refund Request
1. Customer creates support case (POST `/support-cases/`)
2. If case_type is "refund", support service creates refund request via refund service
3. Support case updated with refund_request_id
4. Refund service processes request and communicates back via comments

### Refund Decision Workflow
1. Agent reviews refund request (GET `/refund-cases/{id}/detailed`)
2. Agent makes decision (POST `/refund-cases/{id}/decisions`)
3. Refund service updates status
4. Support service notified via comment system
5. Support case timeline updated

## Error Handling

Both services return standard HTTP status codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **403**: Forbidden (access denied)
- **404**: Not Found
- **500**: Internal Server Error

## Authentication & Authorization

- Currently supports role-based access control (customer vs agent)
- Support cases can only be updated by the owning customer
- Agent endpoints require appropriate authorization

## Frontend Integration

The frontend uses two main API clients:
- `supportApi` - For support service interactions
- `refundApi` - For refund service interactions

Both are configured to handle errors and provide appropriate feedback to users.

## Development Commands

```bash
# Start Support Service
cd support-service && python src/run.py

# Start Refund Service  
cd refund-service && python src/run.py

# Start Frontend
cd frontend && npm run dev
```

## Testing

- API endpoints can be tested via frontend application
- Direct API testing via http://localhost:8001/docs and http://localhost:8002/docs
- Mock data available via scripts/mock_data.py

## Configuration

- Service ports: Support (8001), Refund (8002)
- Database files: `data/support.db`, `data/refund.db`
- CORS configured for local development