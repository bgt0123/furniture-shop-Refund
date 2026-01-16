# Quick Start Guide: Customer Support and Refund Microservice

## Prerequisites

- Python 3.12+
- Node.js 18+
- SQLite 3
- Redis 7+
- Git

## Setup Instructions

### 1. Clone and Initialize
```bash
git clone <repository-url>
cd furniture-shop-Refund
git checkout 1-support-refund
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Initialize database
python -m alembic upgrade head

# Run tests
pytest tests/ --cov=src --cov-report=html

# Start development server
uvicorn src.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Run tests
npm test

# Start development server
npm run dev
```

### 4. Environment Configuration

Create `.env` file in backend directory:
```env
DATABASE_URL=sqlite:///./support_refund.db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
ORDER_API_BASE_URL=http://localhost:8080
PAYMENT_API_BASE_URL=http://localhost:8081
```

## API Endpoints

### Support Cases
- `GET /api/v1/support-cases` - List support cases
- `POST /api/v1/support-cases` - Create support case
- `GET /api/v1/support-cases/{case_id}` - Get case details
- `PATCH /api/v1/support-cases/{case_id}` - Update case
- `PUT /api/v1/support-cases/{case_id}/status` - Update status

### Refund Cases
- `GET /api/v1/support-cases/{case_id}/refund-cases` - List refund cases
- `POST /api/v1/support-cases/{case_id}/refund-cases` - Create refund case
- `POST /api/v1/refund-cases/{refund_case_id}/approve` - Approve refund
- `POST /api/v1/refund-cases/{refund_case_id}/process` - Process refund

### Authentication
- `POST /api/v1/auth/login` - Customer login
- `POST /api/v1/auth/support-login` - Support agent login

## Testing Strategy

### Backend Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/

# Coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

### Frontend Tests
```bash
# Unit tests
npm run test:unit

# Integration tests  
npm run test:integration

# End-to-end tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

## Development Workflow

1. **Feature Development**: Work on feature branch following DDD patterns
2. **Testing**: Implement tests before code following TDD approach
3. **Code Review**: Submit PR with ≥80% test coverage
4. **Integration**: Merge after CI/CD pipeline passes

## Domain-Driven Design Structure

### Domain Layer
- **Entities**: SupportCase, RefundCase, RefundLineItem
- **Value Objects**: MonetaryAmount, DeliveryWindowValidation
- **Aggregates**: SupportCase Aggregate
- **Domain Services**: RefundEligibilityService, PaymentProcessingService

### Application Layer
- **Use Cases**: CreateSupportCase, RequestRefund, ApproveRefund
- **Services**: Application services orchestrating domain logic

### Infrastructure Layer
- **Database**: SQLAlchemy models and repositories
- **External APIs**: Order system integration, Payment gateway
- **Authentication**: JWT-based RBAC implementation

### API Layer
- **Endpoints**: RESTful API with OpenAPI documentation
- **Middleware**: Authentication, rate limiting, error handling

## Key Business Rules

### Support Cases
- Cases must be linked to valid customer orders
- Status transitions follow logical workflow
- History tracking for all actions and state changes

### Refund Cases
- Can only be created from open support cases
- Must be processed within 14 days of delivery
- Support partial refunds by product and quantity
- Single-level approval workflow

### Delivery Validation
- Delivery dates sourced from external order system
- Real-time validation of 14-day window
- Automatic rejection of expired refund requests

## Performance Considerations

- API response time <500ms
- Redis caching for frequent queries
- Database indexing on critical fields
- Async processing for external API calls

## Monitoring and Observability

- Structured logging for all operations
- Performance metrics collection
- Error tracking and alerting
- Audit trail for all financial transactions