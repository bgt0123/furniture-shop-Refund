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

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

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

<!-- MANUAL ADDITIONS END -->
