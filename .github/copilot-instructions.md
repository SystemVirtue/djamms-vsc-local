<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## DJAMMS Full-Stack Development Guidelines

This workspace encompasses both DJAMMS backend development (FastAPI, PostgreSQL, Redis, Cloudflare R2) and frontend UI integration with the base44.Handmade_Repo. Prioritize scalable, production-grade code, robust API design, and seamless full-stack integration.

### Architecture Principles
- Implement proper separation of concerns with routes, services, and models
- Use dependency injection for testable and maintainable code
- Maintain async-first development approach with FastAPI
- Design RESTful APIs that align with frontend requirements

### Backend Development
- Use SQLAlchemy ORM with proper relationship modeling
- Implement migrations with Alembic
- Use Pydantic for robust schema validation
- Implement efficient caching with Redis
- Configure CORS properly for local development and production

### Frontend Integration
- Create responsive React components that consume backend APIs
- Implement WebSocket connections for real-time features
- Use proper state management with React hooks or context
- Follow the established UI design system
- Ensure accessibility compliance

### API Contract
- Maintain consistent API response formats
- Document all endpoints thoroughly
- Version APIs appropriately
- Implement proper error handling with informative responses
- Support frontend pagination and filtering requirements

### Media Player Implementation
- Support both Spotify and YouTube media sources
- Implement FFmpeg for audio/video processing
- Design WebSocket events for player state synchronization
- Support playlist conversion between media sources

### Security Best Practices
- Use JWT authentication with proper token refresh
- Implement role-based access control
- Sanitize all user inputs
- Store credentials in environment variables only
- Protect against XSS, CSRF, and SQL injection

### Testing Strategy
- Write backend unit tests with pytest
- Implement frontend component tests with React Testing Library
- Create end-to-end tests with Cypress
- Maintain high test coverage for critical paths

### Build & Deployment
- Configure proper build pipelines for both frontend and backend
- Implement Docker containerization
- Set up CI/CD with GitHub Actions
- Create comprehensive health checks
- Use infrastructure as code for cloud deployments

### Developer Experience
- Monitor terminal output for errors and implement auto-recovery
- Maintain clear documentation for both frontend and backend
- Establish consistent code formatting and linting rules
- Create helper scripts for common development tasks