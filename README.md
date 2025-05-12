# AI-Enhanced Video Surveillance System

A full-featured FastAPI application for video surveillance systems with external AI integration.

## Features

- User management with roles and permissions
- Location (buildings) management
- Surveillance camera management
- Video storage and management
- Incident detection using AI
- JWT authentication

## Technologies

- Python 3.10+
- FastAPI
- SQLAlchemy 2.0+
- Pydantic 2.0+
- Alembic for migrations
- JWT for authentication

## Installation

1. Clone the repository

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables (or use a `.env` file)

4. Run migrations:
```
alembic upgrade head
```

5. Start the server:
```
uvicorn app.main:app --reload
```

6. Open Swagger UI:
```
http://localhost:8000/docs
```

## Project Structure

```
app/                   # Main application package
├── db/                # Database configuration and utils
│   ├── session.py     # Database connection setup
│   ├── base.py        # Base models and database utilities
│   └── init_models.py # Model initialization
├── common/            # Shared utilities and components
│   ├── repository.py  # Base repository pattern implementation
│   ├── schemas.py     # Common Pydantic schemas
│   ├── dependencies.py # FastAPI dependencies
│   └── utils.py       # General utility functions
├── auth/              # Authentication & authorization module
│   ├── dependencies.py # Auth dependencies
│   ├── models.py      # Auth database models (roles, permissions)
│   ├── router.py      # Auth endpoints
│   ├── schemas.py     # Auth Pydantic schemas
│   ├── service.py     # Auth business logic
│   └── repository.py  # Auth data access layer
├── users/             # User management module
│   ├── models.py      # User database models
│   ├── router.py      # User endpoints
│   ├── schemas.py     # User Pydantic schemas
│   ├── service.py     # User business logic
│   └── repository.py  # User data access layer
├── locations/         # Locations/buildings management
│   ├── models.py      # Location database models
│   ├── router.py      # Location endpoints
│   ├── schemas.py     # Location Pydantic schemas
│   ├── service.py     # Location business logic
│   └── repository.py  # Location data access layer
├── cameras/           # Camera management module
│   ├── models.py      # Camera database models
│   ├── router.py      # Camera endpoints
│   ├── schemas.py     # Camera Pydantic schemas
│   ├── service.py     # Camera business logic
│   └── repository.py  # Camera data access layer
├── videos/            # Video management module
│   ├── models.py      # Video database models
│   ├── router.py      # Video endpoints
│   ├── schemas.py     # Video Pydantic schemas
│   ├── service.py     # Video business logic
│   └── repository.py  # Video data access layer
├── events/            # Event detection and management
│   ├── models.py      # Event database models
│   ├── router.py      # Event endpoints
│   ├── schemas.py     # Event Pydantic schemas
│   ├── service.py     # Event business logic
│   └── repository.py  # Event data access layer
├── config.py          # Application configuration
└── main.py            # Application entry point
``` 