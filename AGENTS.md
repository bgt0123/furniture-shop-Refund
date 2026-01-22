# Furniture-Shop Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-17

## Active Technologies

- Python 3.12+, TypeScript 5.4+ + FastAPI, React 18, SQLite, Redis (001-support-refund-workflow)

## Project Structure

```text
src/
tests/
```

## Commands

**Python Services:**
- `cd support-service && python src/run.py` - Start Support Service (port 8001)
- `cd refund-service && python src/run.py` - Start Refund Service (port 8002)
- `ruff check .` - Lint Python code
- `pytest` - Run tests (currently no tests available)

**Frontend (React):**
- `cd frontend && npm run dev` - Start development server

**API Testing:**
- Support Service: http://localhost:8001/support-cases
- Refund Service: http://localhost:8002/refund-cases

## Code Style

Python 3.12+, TypeScript 5.4+: Follow standard conventions

## Recent Changes

- 001-support-refund-workflow: Added Python 3.12+, TypeScript 5.4+ + FastAPI, React 18, SQLite, Redis

<!-- MANUAL ADDITIONS START -->

## Updated Refund Workflow Design

**Key Changes in 001-support-refund-workflow**:
- RefundRequest now properly belongs to Refund Service domain, not Support Service
- SupportCase has case_type field (Question/Refund) to distinguish case purpose
- When creating refund cases, Support Service calls Refund Service API
- Clear separation of service responsibilities maintained

**Service Boundaries**:
- **Support Service**: Manages SupportCase lifecycle and general support interactions
- **Refund Service**: Manages RefundRequest lifecycle, validation, and refund processing

## Enhanced Refund Status Display

**Recent Enhancement**: Support case detail view now displays comprehensive refund request information including:
- Visual refund status badges with appropriate icons and colors
- Detailed refund case information (Order ID, creation/update dates)
- Improved error handling for timing issues between services
- Better user experience with loading states and clear status indicators

**Refund Status Values**:
- ⏳ Pending Review (yellow)
- ✅ Approved (green) 
- ❌ Rejected (red)
- ❓ Unknown Status (gray)

## Fixes for Refund Status Persistence and Display

**Issues Resolved**:
- **Status not showing up**: Fixed database path configuration in refund-service/src/infrastructure/config.py
- **Approval doesn't persist**: Added proper transaction handling and refetching logic in frontend
- **Frontend refresh after status changes**: Enhanced status update handlers to wait briefly and refetch data

**Technical Changes**:
- Refund service database path changed from `/app/data/refund.db` to `data/refund.db` for development
- Support service database path changed from `/app/data/support.db` to `data/support.db` for development  
- Frontend API calls now refetch data after status updates to ensure UI consistency

**Testing Status**: ✅ All backend API endpoints working correctly with persistent status updates

<!-- MANUAL ADDITIONS END -->
