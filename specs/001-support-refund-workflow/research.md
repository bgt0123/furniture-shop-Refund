# Technical Research: Support and Refund Service Workflow

## Summary
This document captures the technical decisions made during the implementation planning phase for the Support and Refund Service feature.

## Key Decisions

### Domain Modeling Approach
**Decision**: Implement separate bounded contexts for Support and Refund domains

**Rationale**: 
- Support domain handles case management, customer communication, and evidence submission
- Refund domain handles eligibility validation, decision making, and financial processing
- Clear separation aligns with microservices architecture and DDD principles

**Alternatives considered**: Single aggregate for support/refund combined - rejected due to violating single responsibility principle

### Frontend Technical Abstraction
**Decision**: Frontend interacts with business-oriented APIs only, no technical IDs exposed

**Rationale**:
- Customers should see meaningful business identifiers (case numbers, product names)
- Avoids exposing database implementation details
- Enhances security by hiding internal system structure

**Alternatives considered**: Direct database ID exposure - rejected as it violates the "no technical details in frontend" requirement

### Context Boundary Clarification
**Decision**: Refund request submission moved to Refund Service API (/api/v1/support-cases/{case_number}/refund-request)

**Rationale**:
- Maintains proper bounded context boundaries
- Consolidates all refund-related operations in Refund Service
- Support Service focuses purely on case management
- Aligns with Single Responsibility Principle

**Alternatives considered**: Leaving endpoint in Support Service - rejected due to violating context boundaries

### Microservices Communication
**Decision**: Refund Service handles refund operations, Support Service manages cases

**Rationale**:
- Clear separation of concerns between domains
- Support Service delegates refund-specific operations to Refund Service
- Maintains loose coupling between services

**Alternatives considered**: Combined endpoints - rejected due to violating DDD principles

### Data Consistency Strategy
**Decision**: Reference data accessed via real-time API calls to shop service

**Rationale**:
- Ensures up-to-date product and order information
- Prevents stale data in support/refund decisions
- Simpler than caching with complex invalidation logic

**Alternatives considered**: Cached reference data - rejected due to complexity and risk of stale decisions

### Database Separation
**Decision**: Separate SQLite databases for each service (support.db, refund.db)

**Rationale**:
- Full separation of bounded contexts at database level
- Each service owns its data model independently
- No cross-service database dependencies
- Better scalability and deployment flexibility

**Alternatives considered**: Shared database with separate schemas - rejected due to tighter coupling and shared infrastructure dependencies

### Authentication & Authorization
**Decision**: Role-based access control with customer self-service and agent approval workflow

**Rationale**:
- Customers can submit cases and view status
- Agents have access to case queues and approval workflows
- Clear separation of concerns between customer and agent interactions

**Alternatives considered**: Free-for-all access - rejected due to security and privacy concerns

## Technology Stack Validation

All technology choices align with the Furniture Web Shop Constitution v3.1.1:
- Python 3.12+ with FastAPI for service APIs
- React 18+ with TypeScript for frontend
- Separate SQLite databases for each service (support.db, refund.db)
- Redis for caching and session management
- Docker containers for development and deployment

## DDD Compliance

Entities planned:
- SupportCase (aggregate root)
- RefundRequest (entity within SupportCase)
- SupportAgent (domain entity)
- Customer (external entity reference)

Following Clean Architecture layers:
- Domain: Business logic and entities
- Application: Use cases and commands
- Infrastructure: External concerns and persistence
- Presentation: API endpoints