# Quickstart Guide: Customer Support and Refund Microservice

**Date**: January 16, 2026
**Version**: 1.0.0

## Prerequisites

- Python 3.12+
- Node.js 18+
- Docker and Docker Compose
- Redis 6+

## Quick Installation

### Option 1: Docker (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd furniture-shop-Refund
   git checkout 1-support-refund
   ```

2. **Environment setup**:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Start services**:
   ```bash
   docker-compose up --build
   ```

### Option 2: Manual Installation

1. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Start Redis**:
   ```bash
   redis-server
   ```

## Initial Setup

### Database Setup

```bash
# Create and migrate database
cd backend
python scripts/init_db.py
python scripts/migrate.py
```

### Create First Support Agent

```bash
python scripts/create_agent.py --email admin@support.com --role admin
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:e2e
```

## API Usage Examples

### Create Support Case

```bash
curl -X POST http://localhost:8000/api/v1/support-cases \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <customer_token>" \
  -d '{
    "customer_id": "uuid",
    "order_id": "uuid", 
    "title": "Damaged Furniture",
    "description": "Chair arrived with broken legs"
  }'
```

### Create Refund Request

```bash
curl -X POST http://localhost:8000/api/v1/support-cases/{case_id}/refund-cases \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <customer_token>" \
  -d '{
    "refund_items": [
      {
        "product_id": "uuid",
        "product_name": "Designer Chair",
        "requested_quantity": 1,
        "original_unit_price": 299.99
      }
    ]
  }'
```

### Approve and Process Refund

```bash
# Approve refund (support agent)
curl -X POST http://localhost:8000/api/v1/refund-cases/{refund_id}/approve \
  -H "Authorization: Bearer <agent_token>"

# Process refund
curl -X POST http://localhost:8000/api/v1/refund-cases/{refund_id}/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <agent_token>" \
  -d '{
    "settlement_reference": "REF-12345",
    "approved_by": "agent_uuid"
  }'
```

## Development Workflow

### Code Structure

```
backend/
├── src/
│   ├── domain/          # DDD entities and value objects
│   ├── application/     # Use cases and services
│   ├── infrastructure/  # Database and external integrations
│   └── api/             # FastAPI endpoints
└── tests/

frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   └── hooks/           # Custom React hooks
└── tests/
```

### Adding New Features

1. **Domain Layer**: Add entities/value objects in `src/domain/`
2. **Application Layer**: Add use cases in `src/application/use_cases/`
3. **Infrastructure**: Add database models in `src/infrastructure/database/`
4. **API Layer**: Add endpoints in `src/api/endpoints/`
5. **Testing**: Add corresponding tests

## Configuration

### Environment Variables

**Backend (.env)**:
```
DATABASE_URL=sqlite:///./support_refund.db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
PAYMENT_GATEWAY_URL=https://api.payment-gateway.com
ORDER_SERVICE_URL=https://api.order-service.com
```

**Frontend (.env)**:
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_AUTH_URL=http://localhost:8000/auth
```

## Monitoring and Debugging

### Logs

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Redis logs
docker-compose logs redis
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/db-health
```

## Troubleshooting

### Common Issues

**Database connection errors**:
- Check database URL in `.env`
- Ensure SQLite file exists and is accessible

**Redis connection errors**:
- Verify Redis is running
- Check Redis URL configuration

**JWT authentication issues**:
- Verify JWT_SECRET_KEY is set
- Check token expiration

**Payment gateway integration**:
- Test with mock implementation first
- Check API credentials

## Next Steps

1. Set up monitoring (Prometheus + Grafana)
2. Configure CI/CD pipeline
3. Set up production deployment
4. Configure SSL certificates
5. Set up backup strategy

## Support

- API Documentation: http://localhost:8000/docs
- Frontend Application: http://localhost:3000
- Test Coverage Reports: `backend/htmlcov/index.html`