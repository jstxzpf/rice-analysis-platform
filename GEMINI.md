# Project: Jiangsu Taixing Rice Growth Intelligent Analysis Platform

## 1. Project Overview

This project is a full-stack web application designed for the intelligent analysis of rice growth. It utilizes a B/S (Browser/Server) architecture with a modern technology stack.

- **Frontend:** A reactive single-page application (SPA) built with **Vue.js 3** and **TypeScript**, using **Vite** for fast development and builds.
- **Backend:** A high-performance asynchronous API server built with **Python** and the **FastAPI** framework.
- **Database:** A **PostgreSQL** database for persistent data storage, managed via **SQLAlchemy**.
- **Task Queuing:** **Celery** with a **Redis** broker is used for handling long-running, asynchronous tasks, such as image analysis.
- **Image Processing:** The backend is equipped with powerful image analysis libraries like **OpenCV**, **scikit-image**, and **Pillow**, indicating that a core feature is the processing and analysis of uploaded images (likely of rice paddies).
- **Containerization:** The entire application stack is containerized using **Docker** and orchestrated with **Docker Compose**, ensuring consistent development and deployment environments.

The system is composed of four main services:
1.  `db`: The PostgreSQL database container.
2.  `redis`: The Redis in-memory data store, serving as the Celery message broker.
3.  `backend`: The FastAPI application container, serving the API.
4.  `worker`: The Celery worker container, responsible for background task execution.

## 2. Building and Running the Project

The entire application is managed via Docker Compose.

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1.  **Navigate to the project root directory:**
    ```bash
    cd rice-analysis-platform
    ```

2.  **Build and start all services in detached mode:**
    ```bash
    docker-compose up --build -d
    ```

This command will:
- Build the `backend` Docker image (tagged as `rice-analysis-platform-backend:latest`).
- Pull the `postgres:15` and `redis:7` images.
- Start all services (`db`, `redis`, `backend`, `worker`) in the background.

### Accessing the Services

- **Backend API:** The FastAPI backend will be accessible at `http://localhost:8000`.
- **API Docs:** Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.
- **Database:** The PostgreSQL database is exposed on `localhost:5432`.
- **Frontend (Development):** To run the frontend in development mode, navigate to the `frontend` directory and run:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    The frontend will be accessible at the URL provided by the Vite development server (usually `http://localhost:5173`).

## 3. Development Conventions

- **Backend:** The backend follows the standard FastAPI project structure, separating concerns into `api`, `core`, `crud`, `db`, `schemas`, and `worker` modules. It uses `Pydantic` for data validation and `SQLAlchemy` for database object-relational mapping.
- **Frontend:** The frontend uses Vue.js 3 with a standard project structure (`src`, `components`, `views`, etc.). It uses TypeScript for type safety.
- **Asynchronous Operations:** Long-running tasks, especially image processing, are offloaded to the Celery worker to avoid blocking the API server. This is a key architectural pattern in this project.
