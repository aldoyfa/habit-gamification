# Habit Gamification API

[![CI/CD Pipeline](https://github.com/nagikaz/habit-gamification/actions/workflows/ci.yml/badge.svg)](https://github.com/nagikaz/habit-gamification/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/nagikaz/habit-gamification/branch/main/graph/badge.svg)](https://codecov.io/gh/nagikaz/habit-gamification)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A RESTful API for habit tracking with gamification features, built with FastAPI and Domain-Driven Design principles.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Development](#-development)
- [Testing](#-testing)
- [Docker Deployment](#-docker-deployment)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **JWT Authentication** - Secure API access with Bearer token authentication
- **Habit Management** - Create and track personal habits
- **Progress Tracking** - Monitor completed vs total entries with percentage calculation
- **Streak System** - Track consecutive completions with automatic reset on missed days
- **User Isolation** - Each user can only access their own habits
- **API Documentation** - Interactive Swagger UI and ReDoc documentation
- **95%+ Test Coverage** - Comprehensive unit and integration tests
- **Docker Support** - Easy deployment with Docker and Docker Compose
- **CI/CD Pipeline** - Automated testing, linting, and deployment

## 🏗 Architecture

This project follows **Domain-Driven Design (DDD)** principles:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (routes.py)                  │
│  - Authentication endpoints                                 │
│  - Protected habit endpoints                                │
│  - Request/Response handling                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Domain Layer (models.py)                  │
│  - Habit (Aggregate Root)                                   │
│  - Progress, Streak (Value Objects)                         │
│  - HabitEntry (Entity)                                      │
│  - User (Entity)                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Repository Layer (repository.py)              │
│  - HabitRepository                                          │
│  - UserRepository                                           │
│  - In-memory storage (easily swappable for database)        │
└─────────────────────────────────────────────────────────────┘
```

### Domain Model

- **User**: Entity for authentication with bcrypt password hashing
- **Habit**: Aggregate root containing all habit information
- **Progress**: Value object tracking completed/total entries
- **Streak**: Value object for consecutive completion tracking
- **HabitEntry**: Entity representing a single daily entry

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip or pipenv
- Docker & Docker Compose (optional)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nagikaz/habit-gamification.git
   cd habit-gamification
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop the service
docker-compose down
```

## 📚 API Documentation

### Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API information | No |
| `POST` | `/api/auth/login` | User login | No |
| `POST` | `/api/habits` | Create a new habit | Yes |
| `GET` | `/api/habits/{habitId}` | Get habit details | Yes |
| `POST` | `/api/habits/{habitId}/complete` | Mark habit as completed | Yes |
| `POST` | `/api/habits/{habitId}/miss` | Mark habit as missed | Yes |
| `GET` | `/api/habits/{habitId}/progress` | Get habit progress | Yes |

### Example Requests

#### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test_password"}'
```

Response:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "Bearer"
}
```

#### Create Habit
```bash
curl -X POST "http://localhost:8000/api/habits" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"title": "Morning Exercise", "description": "30 minutes daily workout"}'
```

Response:
```json
{
  "habitId": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Morning Exercise",
  "description": "30 minutes daily workout",
  "progress": {
    "completedEntries": 0,
    "totalEntries": 0,
    "percentage": 0
  },
  "streak": {
    "count": 0
  },
  "created_at": "2026-01-09T10:00:00",
  "updated_at": "2026-01-09T10:00:00"
}
```

#### Complete Habit
```bash
curl -X POST "http://localhost:8000/api/habits/{habitId}/complete" \
  -H "Authorization: Bearer <your-token>"
```

#### Get Progress
```bash
curl -X GET "http://localhost:8000/api/habits/{habitId}/progress" \
  -H "Authorization: Bearer <your-token>"
```

Response:
```json
{
  "progress": {
    "completedEntries": 10,
    "totalEntries": 14,
    "percentage": 71
  },
  "streak": {
    "count": 4
  }
}
```

## 🔐 Authentication

The API uses JWT (JSON Web Token) for authentication. All habit endpoints require a valid Bearer token.

### Getting a Token

1. A test user is created automatically on startup:
   - Username: `test_user`
   - Password: `test_password`

2. Call the login endpoint to get a token:
   ```bash
   POST /api/auth/login
   {
     "username": "test_user",
     "password": "test_password"
   }
   ```

3. Include the token in subsequent requests:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

### Token Configuration

- Algorithm: HS256
- Expiration: 30 minutes
- Secret key should be changed in production (see `app/auth.py`)

## 💻 Development

### Code Style

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for linting issues
ruff check app/ tests/

# Auto-fix linting issues
ruff check --fix app/ tests/

# Check formatting
ruff format --check app/ tests/

# Apply formatting
ruff format app/ tests/
```

### Pre-commit Setup (Optional)

```bash
pip install pre-commit
pre-commit install
```

## 🧪 Testing

The project maintains **95%+ test coverage** with comprehensive unit and integration tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run with coverage and fail under 95%
pytest --cov=app --cov-report=term-missing --cov-fail-under=95

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_models.py::TestHabit

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Fixtures and configuration
├── test_models.py       # Domain model tests
├── test_repository.py   # Repository layer tests
├── test_auth.py         # Authentication tests
├── test_schemas.py      # Schema validation tests
└── test_routes.py       # API integration tests
```

### Running Tests in Docker

```bash
docker-compose --profile test run test
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Using Docker Only

```bash
# Build image
docker build -t habit-gamification:latest .

# Run container
docker run -d -p 8000:8000 --name habit-api habit-gamification:latest

# Check logs
docker logs -f habit-api

# Stop container
docker stop habit-api
docker rm habit-api
```

### Health Check

The container includes a health check that verifies the API is responding:

```bash
docker inspect --format='{{.State.Health.Status}}' habit-gamification-api
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) includes:

1. **Lint** - Code quality checks with Ruff
2. **Test** - Run tests with 95% coverage requirement
3. **Build** - Build and test Docker image
4. **Deploy** - Push to GitHub Container Registry (on main/master branch)

### Pipeline Stages

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐
│  Lint   │ ──▶ │   Test   │ ──▶ │  Build  │ ──▶ │  Deploy  │
└─────────┘     └──────────┘     └─────────┘     └──────────┘
     │               │                │               │
     │               │                │               │
   Ruff           Pytest          Docker         GHCR Push
  Check          95% cov         Image Test    (main only)
```

### Badge Status

The CI/CD badge at the top of this README shows the current pipeline status. A green checkmark (✓) indicates all tests are passing.

## 📁 Project Structure

```
habit-gamification/
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline configuration
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Domain models (DDD)
│   ├── repository.py        # Data access layer
│   ├── routes.py            # API endpoints
│   ├── schemas.py           # Pydantic request/response models
│   └── auth.py              # JWT authentication
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_models.py       # Domain model tests
│   ├── test_repository.py   # Repository tests
│   ├── test_auth.py         # Authentication tests
│   ├── test_schemas.py      # Schema validation tests
│   └── test_routes.py       # API integration tests
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml           # Project configuration (ruff, pytest)
├── requirements.txt
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check app/ tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Maintain 95%+ test coverage
- Follow the existing code style (enforced by Ruff)
- Write meaningful commit messages
- Update documentation for new features
- Add tests for new functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ using FastAPI and Domain-Driven Design