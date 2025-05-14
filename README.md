# SecAppAI: AI-Enhanced Video Surveillance System (Monorepo)

This monorepo contains the complete codebase for the SecAppAI project, an AI-enhanced video surveillance system.

## Components

This project is organized into the following main components:

*   `backend/`: The core FastAPI backend service.
    *   Handles API requests, user management, database interactions, and business logic.
    *   (See `backend/README.md` for detailed setup and usage instructions)
*   `frontend/`: Frontend web application for user interaction.
*   `ai_service/`: Dedicated service for AI model inference and video processing.
*   `docs/`: Project documentation, including API specifications, architecture diagrams, and setup guides.
*   `scripts/`: Utility scripts for development, testing, and deployment across the monorepo.

## Core Technologies (Overall Project)

*   Python (for backend)
*   FastAPI (for backend API)
*   PostgreSQL (Database)
*   Alembic (Database migrations)
*   Pydantic (Data validation)
*   JWT (Authentication)

## Getting Started

1.  **Clone the monorepo:**
    ```bash
    git clone https://github.com/vdals/SecAIApp.git
    cd SecAppAI
    ```

2.  **Setup Individual Components:**
    Each component (`backend`, `frontend`, `ai_service`) has its own setup instructions, dependencies, and virtual environment. Please refer to the `README.md` file within each component's directory for detailed setup.

    *   To set up the backend, navigate to the `backend/` directory and follow the instructions in `backend/README.md`.

## Project Structure Overview

```
SecAppAI/
├── backend/
├── frontend/
├── ai_service/
├── docs/
├── scripts/
├── .gitignore
├── README.md