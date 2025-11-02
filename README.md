# Wallet API

A FastAPI-based wallet management system with PostgreSQL.

## Features

- Create and manage digital wallets
- Deposit and withdraw funds
- Concurrent operation handling
- RESTful API
- Docker containerization
- Comprehensive testing

## CI/CD Status

![CI/CD](https://github.com/your-username/wallet-api/workflows/CI/CD%20for%20Wallet%20API/badge.svg)
![Code Coverage](https://img.shields.io/codecov/c/github/your-username/wallet-api)

## API Documentation

Once running, visit `/docs` for interactive API documentation.

## Development

### Local Setup

1. Clone the repository
2. Run with Docker Compose:
\\`\\`\\`bash
docker-compose up --build
\\`\\`\\`

3. Run tests:
\\`\\`\\`bash
docker-compose exec web pytest tests/ -v
\\`\\`\\`

### Code Quality

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking
- **pytest**: Testing with coverage

## License

MIT