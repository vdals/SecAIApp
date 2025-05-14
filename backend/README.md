# AI-Enhanced Video Surveillance System (Backend)

This is the backend component for the SecAppAI project, a full-featured FastAPI application for video surveillance systems with external AI integration.

## Features

- User management with roles and permissions
- Location (buildings) management
- Surveillance camera management
- Video storage and management
- Incident detection using AI
- JWT authentication

## Technologies Used in Backend

- Python 3.10+
- FastAPI
- SQLAlchemy 2.0+
- Pydantic 2.0+
- Alembic for migrations
- JWT for authentication
- PostgreSQL (Database)

## Backend Setup and Installation

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the `backend/` directory by copying `backend/.env.example` or by setting the variables manually.

4.  **Run database migrations:**
    Ensure your PostgreSQL server is running and accessible.
    ```bash
    alembic upgrade head
    ```

5.  **Start the backend server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will typically run on `http://localhost:8000`.

6.  **Access API Documentation (Swagger UI):**
    Open your browser and go to `http://localhost:8000/docs`.

## Backend Project Structure

```
backend/
├── app/                   # Main application package
│   ├── db/                # Database configuration and utils
│   │   ├── session.py     # Database connection setup
│   │   ├── base.py        # Base models and database utilities
│   │   └── init_models.py # Model initialization
│   ├── common/            # Shared utilities and components
│   │   ├── repository.py  # Base repository pattern implementation
│   │   ├── schemas.py     # Common Pydantic schemas
│   │   ├── dependencies.py # FastAPI dependencies
│   │   └── utils.py       # General utility functions
│   ├── auth/              # Authentication & authorization module
│   │   ├── ...            # (models, router, schemas, service, repository)
│   ├── users/             # User management module
│   │   ├── ...
│   ├── locations/         # Locations/buildings management
│   │   ├── ...
│   ├── cameras/           # Camera management module
│   │   ├── ...
│   ├── videos/            # Video management module
│   │   ├── ...
│   ├── events/            # Event detection and management
│   │   ├── ...
│   ├── config.py          # Application configuration
│   └── main.py            # Application entry point
├── alembic/               # Alembic migration scripts
├── alembic.ini            # Alembic configuration
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables
``` 