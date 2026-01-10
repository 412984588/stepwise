# Code Review Checklist

> Comprehensive code review checklist based on industry best practices

**Purpose**: Ensure code quality, security, maintainability, and adherence to project standards before merging.

**Automation**: Many items can be automated using tools (see [Automation Recommendations](#automation-recommendations))

---

## Table of Contents

1. [Logic & Correctness](#1-logic--correctness)
2. [Design & Architecture](#2-design--architecture)
3. [Security](#3-security)
4. [Dependencies & External Libraries](#4-dependencies--external-libraries)
5. [Secrets & Credentials](#5-secrets--credentials)
6. [Testing](#6-testing)
7. [Performance](#7-performance)
8. [Code Style & Readability](#8-code-style--readability)
9. [Documentation](#9-documentation)
10. [Error Handling](#10-error-handling)
11. [Database & Data](#11-database--data)
12. [API Design](#12-api-design)
13. [Frontend Specific](#13-frontend-specific)
14. [Backend Specific](#14-backend-specific)

---

## 1. Logic & Correctness

### Core Functionality
- [ ] **Does the code do what it's supposed to do?**
  - Verify against requirements/user story
  - Check edge cases and boundary conditions
  - Validate input/output behavior

- [ ] **Are there any logical errors or bugs?**
  - Off-by-one errors
  - Null/undefined handling
  - Type coercion issues
  - Race conditions

- [ ] **Are all code paths tested?**
  - Happy path
  - Error paths
  - Edge cases

### Business Logic
- [ ] **Does the implementation match business requirements?**
- [ ] **Are calculations and algorithms correct?**
- [ ] **Are there any hardcoded values that should be configurable?**

**🤖 Automation**: Unit tests, integration tests, property-based testing

---

## 2. Design & Architecture

### Code Organization
- [ ] **Is the code in the right place?**
  - Correct module/package
  - Appropriate layer (API, service, model)
  - Follows project structure conventions

- [ ] **Is the code modular and reusable?**
  - Single Responsibility Principle
  - Don't Repeat Yourself (DRY)
  - Separation of Concerns

- [ ] **Are abstractions appropriate?**
  - Not over-engineered
  - Not under-engineered
  - Clear interfaces

### Design Patterns
- [ ] **Are design patterns used appropriately?**
- [ ] **Is dependency injection used where appropriate?**
- [ ] **Are there circular dependencies?** (should be avoided)

### Scalability
- [ ] **Will this code scale?**
  - Database query efficiency
  - Memory usage
  - CPU usage

**🤖 Automation**: Static analysis tools, architecture linters, dependency analyzers

---

## 3. Security

### Input Validation
- [ ] **Is all user input validated?**
  - Type checking
  - Range checking
  - Format validation
  - Sanitization

- [ ] **Are there SQL injection vulnerabilities?**
  - Use parameterized queries
  - ORM usage correct

- [ ] **Are there XSS vulnerabilities?**
  - Output encoding
  - Content Security Policy
  - Sanitize HTML

- [ ] **Are there CSRF vulnerabilities?**
  - CSRF tokens present
  - SameSite cookies

### Authentication & Authorization
- [ ] **Is authentication required where needed?**
- [ ] **Is authorization checked properly?**
  - Role-based access control
  - Resource ownership verification

- [ ] **Are passwords handled securely?**
  - Hashed (not encrypted)
  - Strong hashing algorithm (bcrypt, Argon2)
  - Salted

### Data Protection
- [ ] **Is sensitive data encrypted?**
  - At rest
  - In transit (HTTPS)

- [ ] **Are there information disclosure risks?**
  - Error messages don't leak sensitive info
  - Stack traces not exposed in production

### OWASP Top 10
- [ ] **Check against OWASP Top 10 vulnerabilities**
  - Injection
  - Broken Authentication
  - Sensitive Data Exposure
  - XML External Entities (XXE)
  - Broken Access Control
  - Security Misconfiguration
  - Cross-Site Scripting (XSS)
  - Insecure Deserialization
  - Using Components with Known Vulnerabilities
  - Insufficient Logging & Monitoring

**🤖 Automation**: SAST tools (Snyk, SonarQube), dependency scanners, security linters

---

## 4. Dependencies & External Libraries

### Dependency Management
- [ ] **Are new dependencies necessary?**
  - Can existing dependencies be used?
  - Is the functionality simple enough to implement ourselves?

- [ ] **Are dependencies up-to-date?**
  - No known vulnerabilities
  - Compatible versions

- [ ] **Are dependencies from trusted sources?**
  - Official npm/PyPI/etc.
  - Reputable maintainers
  - Active maintenance

### License Compliance
- [ ] **Are dependency licenses compatible with our project?**
  - MIT, Apache 2.0, BSD (usually OK)
  - GPL, AGPL (may have restrictions)

- [ ] **Are license files included?**

### Dependency Size
- [ ] **Is the dependency size reasonable?**
  - Bundle size impact (frontend)
  - Installation time (backend)

**🤖 Automation**: Dependabot, Snyk, npm audit, pip-audit, license checkers

---

## 5. Secrets & Credentials

### Secret Detection
- [ ] **Are there any hardcoded secrets?**
  - API keys
  - Passwords
  - Tokens
  - Private keys
  - Database credentials

- [ ] **Are secrets stored securely?**
  - Environment variables
  - Secret management service (AWS Secrets Manager, HashiCorp Vault)
  - Not in version control

### Configuration
- [ ] **Are sensitive configs in `.env` files?**
- [ ] **Is `.env` in `.gitignore`?**
- [ ] **Is there a `.env.example` file?**

### Logging
- [ ] **Are secrets logged?** (should NOT be)
  - Check log statements
  - Check error messages
  - Check debug output

**🤖 Automation**: git-secrets, trufflehog, GitHub secret scanning, pre-commit hooks

---

## 6. Testing

### Test Coverage
- [ ] **Are there tests for new code?**
  - Unit tests
  - Integration tests
  - E2E tests (if applicable)

- [ ] **Do tests cover edge cases?**
  - Null/undefined
  - Empty arrays/objects
  - Boundary values
  - Error conditions

- [ ] **Are tests meaningful?**
  - Not just for coverage
  - Actually test behavior
  - Clear test names

### Test Quality
- [ ] **Are tests independent?**
  - No shared state
  - Can run in any order

- [ ] **Are tests deterministic?**
  - No flaky tests
  - No time-dependent tests (unless mocked)

- [ ] **Are mocks/stubs used appropriately?**
  - External services mocked
  - Database mocked (for unit tests)

### Test-Driven Development
- [ ] **Were tests written first?** (TDD)
- [ ] **Do tests fail before implementation?**
- [ ] **Do tests pass after implementation?**

**🤖 Automation**: pytest, Jest, Playwright, coverage tools (pytest-cov, Istanbul)

---

## 7. Performance

### Efficiency
- [ ] **Are there performance bottlenecks?**
  - N+1 queries
  - Unnecessary loops
  - Inefficient algorithms

- [ ] **Are database queries optimized?**
  - Proper indexes
  - Avoid SELECT *
  - Pagination for large datasets

- [ ] **Is caching used appropriately?**
  - Redis/Memcached
  - HTTP caching headers
  - Memoization

### Resource Usage
- [ ] **Is memory usage reasonable?**
  - No memory leaks
  - Large objects cleaned up

- [ ] **Are there unnecessary API calls?**
  - Batch requests where possible
  - Debounce/throttle user actions

**🤖 Automation**: Profilers, performance monitoring (Sentry, New Relic), load testing

---

## 8. Code Style & Readability

### Naming
- [ ] **Are names descriptive and meaningful?**
  - Variables: `userEmail` not `ue`
  - Functions: `calculateTotalPrice()` not `calc()`
  - Classes: `UserRepository` not `UR`

- [ ] **Do names follow project conventions?**
  - camelCase vs snake_case
  - PascalCase for classes
  - UPPER_CASE for constants

### Code Clarity
- [ ] **Is the code easy to understand?**
  - Clear logic flow
  - Not overly clever
  - Appropriate comments

- [ ] **Are functions/methods small and focused?**
  - Single responsibility
  - < 50 lines (guideline)

- [ ] **Is nesting depth reasonable?**
  - < 4 levels deep
  - Early returns to reduce nesting

### Comments
- [ ] **Are comments helpful?**
  - Explain "why", not "what"
  - No commented-out code
  - No TODO comments (use issue tracker)

**🤖 Automation**: ESLint, Ruff, Black, Prettier, markdownlint

---

## 9. Documentation

### Code Documentation
- [ ] **Are complex functions documented?**
  - Docstrings (Python)
  - JSDoc (JavaScript/TypeScript)
  - Type hints

- [ ] **Is the API documented?**
  - OpenAPI/Swagger
  - Request/response examples
  - Error codes

### User Documentation
- [ ] **Is README.md updated?**
  - New features documented
  - Setup instructions current

- [ ] **Are breaking changes documented?**
  - CHANGELOG.md
  - Migration guide

### Inline Documentation
- [ ] **Are magic numbers explained?**
- [ ] **Are complex algorithms explained?**
- [ ] **Are assumptions documented?**

**🤖 Automation**: Documentation generators (Sphinx, JSDoc), API doc tools (Swagger)

---

## 10. Error Handling

### Error Handling Strategy
- [ ] **Are errors handled appropriately?**
  - Try/catch blocks
  - Error boundaries (React)
  - Graceful degradation

- [ ] **Are error messages helpful?**
  - User-friendly (for users)
  - Detailed (for developers)
  - Actionable

- [ ] **Are errors logged?**
  - Sentry/error tracking
  - Appropriate log level
  - Structured logging

### Error Recovery
- [ ] **Can the system recover from errors?**
  - Retry logic
  - Fallback mechanisms
  - Circuit breakers

- [ ] **Are errors propagated correctly?**
  - Not swallowed silently
  - Proper error types

**🤖 Automation**: Sentry, error monitoring, log aggregation (ELK, Datadog)

---

## 11. Database & Data

### Data Integrity
- [ ] **Are database constraints used?**
  - NOT NULL
  - UNIQUE
  - FOREIGN KEY
  - CHECK constraints

- [ ] **Are transactions used where needed?**
  - ACID properties
  - Rollback on error

- [ ] **Is data validated before saving?**
  - Type checking
  - Business rules

### Migrations
- [ ] **Are database migrations reversible?**
  - Down migrations
  - Safe to rollback

- [ ] **Are migrations tested?**
  - On staging environment
  - With production-like data

### Data Privacy
- [ ] **Is PII (Personally Identifiable Information) handled correctly?**
  - GDPR compliance
  - COPPA compliance (for children's data)
  - Data retention policies

**🤖 Automation**: Database migration tools (Alembic, Flyway), data validation libraries

---

## 12. API Design

### RESTful Principles
- [ ] **Are REST conventions followed?**
  - GET for retrieval
  - POST for creation
  - PUT/PATCH for updates
  - DELETE for deletion

- [ ] **Are HTTP status codes correct?**
  - 200 OK
  - 201 Created
  - 400 Bad Request
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 500 Internal Server Error

### API Versioning
- [ ] **Is API versioning used?**
  - `/api/v1/...`
  - Backward compatibility

### Request/Response
- [ ] **Are request/response formats consistent?**
  - JSON structure
  - Error format
  - Pagination format

- [ ] **Is input validation comprehensive?**
  - Required fields
  - Type validation
  - Format validation

**🤖 Automation**: OpenAPI validators, API testing tools (Postman, Insomnia)

---

## 13. Frontend Specific

### React/TypeScript
- [ ] **Are hooks used correctly?**
  - useEffect dependencies
  - useMemo/useCallback for performance
  - Custom hooks for reusability

- [ ] **Is state management appropriate?**
  - Local state vs global state
  - Context API vs Redux/Zustand

- [ ] **Are components accessible?**
  - ARIA labels
  - Keyboard navigation
  - Screen reader support

### Performance
- [ ] **Is code splitting used?**
  - Lazy loading
  - Dynamic imports

- [ ] **Are images optimized?**
  - Appropriate formats (WebP, AVIF)
  - Lazy loading
  - Responsive images

### User Experience
- [ ] **Is loading state handled?**
  - Spinners/skeletons
  - Optimistic updates

- [ ] **Is error state handled?**
  - Error boundaries
  - User-friendly messages

**🤖 Automation**: ESLint (React hooks), Lighthouse, axe DevTools

---

## 14. Backend Specific

### Python/FastAPI
- [ ] **Are type hints used?**
  - Function parameters
  - Return types
  - mypy validation

- [ ] **Is async/await used correctly?**
  - Async database calls
  - Async HTTP requests
  - No blocking operations in async functions

### API Endpoints
- [ ] **Is rate limiting implemented?**
- [ ] **Is CORS configured correctly?**
- [ ] **Are API keys protected?**

### Background Jobs
- [ ] **Are long-running tasks async?**
  - Celery/RQ
  - Background workers

- [ ] **Are jobs idempotent?**
  - Can be retried safely

**🤖 Automation**: mypy, Ruff, pytest, FastAPI test client

---

## Automation Recommendations

### Static Analysis
- **ShellCheck**: Shell script linting
- **markdownlint**: Markdown linting
- **ESLint**: JavaScript/TypeScript linting
- **Ruff**: Python linting (fast)
- **Black**: Python code formatting
- **Prettier**: JavaScript/TypeScript/CSS formatting
- **mypy**: Python type checking

### Security
- **Snyk**: Dependency vulnerability scanning
- **git-secrets**: Prevent committing secrets
- **trufflehog**: Find secrets in git history
- **GitHub secret scanning**: Automatic secret detection
- **Bandit**: Python security linter
- **npm audit**: JavaScript dependency audit

### Testing
- **pytest**: Python testing framework
- **Jest**: JavaScript testing framework
- **Playwright**: E2E testing
- **pytest-cov**: Python coverage
- **Istanbul**: JavaScript coverage

### Code Review
- **reviewdog**: Automated code review comments
- **CodeClimate**: Code quality analysis
- **SonarQube**: Code quality and security
- **Codecov**: Coverage tracking

### CI/CD Integration
- **GitHub Actions**: Workflow automation
- **pre-commit**: Git hooks for local checks
- **Husky**: Git hooks for JavaScript projects

---

## Review Process

### Before Requesting Review
1. **Self-review your code**
   - Read through all changes
   - Check against this checklist
   - Run tests locally
   - Run linters locally

2. **Write a clear PR description**
   - What changed and why
   - How to test
   - Screenshots (if UI changes)
   - Breaking changes

3. **Ensure CI passes**
   - All tests green
   - No linting errors
   - Coverage maintained

### During Review
1. **Respond to comments promptly**
2. **Ask questions if unclear**
3. **Don't take feedback personally**
4. **Explain your reasoning**

### After Review
1. **Address all comments**
2. **Re-request review if needed**
3. **Squash commits if requested**
4. **Merge when approved**

---

## Checklist Summary

Use this quick checklist for every PR:

- [ ] Logic is correct and tested
- [ ] Design follows project patterns
- [ ] No security vulnerabilities
- [ ] Dependencies are necessary and secure
- [ ] No hardcoded secrets
- [ ] Tests added and passing
- [ ] Performance is acceptable
- [ ] Code is readable and well-named
- [ ] Documentation is updated
- [ ] Errors are handled properly
- [ ] Database changes are safe
- [ ] API design is consistent
- [ ] Frontend is accessible (if applicable)
- [ ] Backend is type-safe (if applicable)

---

## References

- [Google Engineering Practices - Code Review](https://google.github.io/eng-practices/review/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [Microsoft Secure Code Review](https://docs.microsoft.com/en-us/azure/security/develop/secure-dev-overview)
- [Thoughtbot Code Review Guide](https://github.com/thoughtbot/guides/tree/main/code-review)
- [Conventional Comments](https://conventionalcomments.org/)

---

*Last Updated: 2026-01-10*  
*Version: 1.0*
