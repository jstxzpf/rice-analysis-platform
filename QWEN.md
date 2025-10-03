# Rice Analysis Platform - Project Context

## Overview

The Rice Analysis Platform is a full-stack web application designed for intelligent analysis of rice growth. It features a B/S (Browser/Server) architecture with a modern technology stack that enables automated analysis of rice paddy images for metrics like coverage, plant height, and growth trends.

### Core Features
- **User & Permission Management**: JWT-based authentication with role-based access
- **Field Management**: Create, edit, and manage multiple rice field records
- **Image Analysis**: Automated processing of drone and ground-level images for rice growth metrics
- **Asynchronous Processing**: Celery-based task queue for non-blocking image analysis
- **Visual Analytics**: Charts and trend analysis of rice growth metrics over time
- **Multi-Platform Support**: Containerized deployment with Docker Compose
- **Advanced Visualization**: Growth heatmap and regional difference analysis
- **Ideal Range Indicators**: Visual indicators for ideal coverage and density ranges
- **Predictive Analytics**: Trend prediction based on historical data
- **Detailed Point Analysis**: Click to view detailed information for data points

## Architecture

### Tech Stack
- **Frontend**: Vue 3 + Vite + TypeScript + Element Plus UI + ECharts
- **Backend**: Python + FastAPI + SQLAlchemy + Pydantic
- **Database**: PostgreSQL 15+
- **Message Queue**: Redis + Celery for asynchronous tasks
- **Image Processing**: OpenCV, scikit-image, Pillow
- **Deployment**: Docker + Docker Compose + Nginx

### System Architecture
```
[User Browser - Vue.js] --> [Nginx - Reverse Proxy] --> [FastAPI Backend]
                                                    --> [Celery Worker]
[Database: PostgreSQL] <-- [FastAPI Backend] <-- [Message Queue: Redis]
```

## Project Structure
```
/rice-analysis-platform
|-- /backend                  # FastAPI Backend
|   |-- /app
|   |   |-- /api              # API endpoints
|   |   |-- /core             # Config and security
|   |   |-- /crud             # Database operations
|   |   |-- /db               # Database models and connection
|   |   |-- /schemas          # Pydantic data models
|   |   |-- /analysis         # Image analysis engine
|   |   |-- /worker           # Celery worker configuration
|   |   |-- main.py           # App entry point
|   |-- requirements.txt
|   |-- Dockerfile
|-- /frontend                 # Vue.js Frontend
|   |-- /src
|   |   |-- /api              # API requests
|   |   |-- /components       # Reusable components
|   |   |-- /views            # Page components
|   |   |-- /router           # Routing
|   |-- package.json
|   |-- Dockerfile
|-- docker-compose.yml        # Docker orchestration
```

## Database Models

### Core Models
- **User**: User accounts with authentication and roles
- **Field**: Rice field records (name, location, area, variety, planting date)
- **PhotoGroup**: Sets of images for analysis (drone, 0.5m side, 3m side photos)
- **AnalysisResult**: Results of image analysis (coverage, height, color indices, etc.)

### Analysis Status
- PENDING: Task queued for processing
- PROCESSING: Currently being analyzed
- COMPLETED: Analysis finished
- FAILED: Analysis failed

## API Endpoints

### Authentication
- `POST /api/v1/token` - User login and JWT token generation
- `GET /api/v1/users/me` - Get current user information

### Field Management
- `POST /api/v1/fields` - Create new field
- `GET /api/v1/fields` - List user fields
- `GET /api/v1/fields/{id}` - Get specific field
- `PUT /api/v1/fields/{id}` - Update field
- `DELETE /api/v1/fields/{id}` - Delete field

### Image Analysis
- `POST /api/v1/photogroups/upload` - Upload images for analysis
- `GET /api/v1/photogroups/status/{task_id}` - Check analysis task status
- `GET /api/v1/fields/{field_id}/results` - Get field analysis results
- `GET /api/v1/results/{result_id}` - Get specific analysis result
- `GET /api/v1/fields/{field_id}/trends` - Get field trend data

### Advanced Visualization
- `GET /api/v1/analysis/growth-heatmap/{field_id}` - Generate growth heatmap data
- `GET /api/v1/analysis/regional-differences/{field_id}` - Analyze regional differences
- `GET /api/v1/analysis/inter-field-comparison/` - Compare metrics across fields

## Key Implementation Details

### Image Analysis Algorithms
1. **Coverage Analysis**: Uses HSV/LAB color space and ExG (excess green) index to calculate canopy coverage
2. **Height Measurement**: Uses whiteboard calibration to determine scale for measuring plant heights
3. **Uniformity Index**: Calculates variation coefficient across grid sections for coverage uniformity
4. **Tiller Density**: Estimates tiller count per unit area using morphological operations
5. **Growth Heatmap**: Generates spatial distribution maps of growth metrics across field areas
6. **Regional Analysis**: Analyzes differences between field quadrants for targeted management
7. **Trend Prediction**: Uses linear regression to forecast growth patterns based on historical data

### Asynchronous Processing Flow
1. User uploads images via frontend
2. Backend saves image files and creates PhotoGroup record with PENDING status
3. Backend triggers Celery task and stores task_id in database
4. Celery worker processes images using analysis engine
5. Analysis results are stored in database and status updated to COMPLETED
6. Frontend polls for status updates to show progress to user

## Development Workflow

### Local Development Setup
```bash
# Navigate to project root
cd rice-analysis-platform

# Build and start all services
docker-compose up --build -d

# For frontend development
cd frontend
npm install
npm run dev
```

### Dependencies
Backend requirements include: fastapi, uvicorn, sqlalchemy, pydantic, psycopg2-binary, redis, celery, opencv-python, scikit-image, Pillow, python-multipart, google-generativeai.

Frontend dependencies include: vue, element-plus, axios, echarts, leaflet, vue-router, vite.

### API Testing
Use the provided `api_test.py` script to test API endpoints:
- Creates a test user
- Authenticates and gets a token
- Tests field management operations
- Tests image upload and analysis triggering

## Deployment

### Production Deployment
The application is designed for containerized deployment using Docker Compose with the following services:
- `db`: PostgreSQL database
- `redis`: Message broker for Celery
- `backend`: FastAPI application server
- `worker`: Celery worker for image analysis
- `frontend`: Vue.js frontend (built and served by Nginx)

### Configuration
- Database credentials and other environment variables are configured via `.env` files
- Nginx handles reverse proxying and static asset serving for the frontend

## Development Conventions

### Backend Practices
- Use Pydantic models for API request/response validation
- Separate concerns into distinct modules (api, core, crud, db, schemas, analysis, worker)
- Use dependency injection for database sessions
- Implement asynchronous processing for long-running tasks
- Follow RESTful API design principles

### Frontend Practices
- Use TypeScript for type safety
- Implement state management with Pinia
- Use Element Plus for UI components
- Create reusable components for common UI elements
- Implement API calls via centralized service modules

## Testing

### API Testing
The project includes `api_test.py` for functional API testing that validates:
- User authentication flow
- Field management operations
- Image upload and processing pipeline
- Asynchronous task handling

## Special Considerations

### Image Processing
The platform relies heavily on computer vision algorithms that may need calibration for different rice varieties, lighting conditions, and image quality. The system uses whiteboard calibration for accurate measurements.

### Scalability
The asynchronous task processing with Celery allows for horizontal scaling of analysis workers based on demand. Redis serves as the message broker for task distribution.

### Security
- JWT tokens for API authentication
- Password hashing using bcrypt
- Input validation via Pydantic models
- Secure session management