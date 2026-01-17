# Quick Start: Support and Refund Service

## Overview
This guide helps developers quickly understand and start working with the Support and Refund Service implementation.

## Architecture

### Service Boundaries
- **Support Service**: Handles customer cases, evidence submission, agent assignment
- **Refund Service**: Manages refund eligibility, decisions, processing, creation
- **Frontend**: Customer and agent interfaces that consume APIs

### DDD Structure
```
support-service/
├── domain/           # Business logic
├── application/      # Use cases
├── infrastructure/   # External concerns
└── presentation/     # API endpoints

refund-service/       # Similar structure

frontend/             # React components and services
```

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- SQLite
- Redis

### Development Setup

1. **Clone and setup services**
```bash
# Support Service
cd support-service
pip install -r requirements.txt
python scripts/setup.py

# Refund Service  
cd refund-service
pip install -r requirements.txt
python scripts/setup.py

# Frontend
cd frontend
npm install
```

2. **Start services**
```bash
# Support Service (port 8001)
cd support-service
uvicorn src.presentation.main:app --port 8001

# Refund Service (port 8002)
cd refund-service  
uvicorn src.presentation.main:app --port 8002

# Frontend (port 3000)
cd frontend
npm run dev
```

## Key APIs

### Support Service Endpoints
- `GET /api/v1/support-cases` - List customer cases
- `POST /api/v1/support-cases` - Create new case

### Refund Service Endpoints
- `POST /api/v1/support-cases/{case_number}/refund-request` - Submit refund request
- `POST /api/v1/refund-request/{id}/approve` - Approve refund
- `POST /api/v1/refund-request/{id}/reject` - Reject refund

## Key Business Rules

### Refund Eligibility
- Must be within 14 days OR product defective
- Only one refund request per support case
- Must provide photographic evidence

### Case Workflow
1. Customer creates support case
2. Submits refund request with photos
3. Agent reviews and makes decision
4. Customer sees status online

## Testing

### Running Tests
```bash
# Support Service
cd support-service
pytest

# Refund Service
cd refund-service
pytest

# Frontend
cd frontend
npm test
```

### Test Coverage
- Domain logic: 100% coverage required
- API endpoints: Integration tests
- Frontend components: Unit tests

## Database Structure

### Support Service Database
```sql
-- Support cases table
CREATE TABLE support_cases (
    case_number TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Refund requests table  
CREATE TABLE refund_requests (
    refund_request_id TEXT PRIMARY KEY,
    case_number TEXT NOT NULL REFERENCES support_cases(case_number),
    status TEXT NOT NULL
);
```

### Important Notes
- No technical IDs exposed to frontend (use business identifiers)
- Real-time references to shop service for products/orders
- Separation between support (customer facing) and refund (business logic) concerns