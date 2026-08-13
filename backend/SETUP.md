# RoadPulse Backend - Setup Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Google Cloud Platform account (for Maps API)
- Anthropic API key (for Claude)
- Firebase project (for push notifications)

## Installation

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Google Maps Platform API Key
GOOGLE_MAPS_API_KEY=your_actual_key_here

# Anthropic API Key
ANTHROPIC_API_KEY=your_actual_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/roadpulse

# Redis
REDIS_URL=redis://localhost:6379

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase_credentials.json
FIREBASE_PROJECT_ID=your-project-id
```

### 4. Set Up PostgreSQL Database

```sql
CREATE DATABASE roadpulse;
CREATE USER roadpulse_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE roadpulse TO roadpulse_user;
```

### 5. Set Up Redis

On Ubuntu/Debian:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

On macOS (with Homebrew):
```bash
brew install redis
brew services start redis
```

### 6. Configure Google Maps Platform

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Routes API
   - Roads API
   - Places API
4. Create an API key and restrict it to your required APIs
5. Add the key to your `.env` file

### 7. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Download service account credentials (JSON)
4. Save as `firebase_credentials.json` in the backend directory
5. Update `FIREBASE_PROJECT_ID` in `.env`

### 8. Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

### 9. Test the API

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

Test health endpoint:
```bash
curl http://localhost:8000/health
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── core/
│   │   └── config.py      # Configuration settings
│   ├── db/
│   │   └── session.py     # Database connection
│   ├── models/
│   │   └── __init__.py    # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── __init__.py    # Pydantic validation schemas
│   ├── api/
│   │   └── routes/
│   │       ├── users.py   # User endpoints
│   │       ├── routes.py  # Route CRUD endpoints
│   │       └── notifications.py  # Notification endpoints
│   └── services/
│       ├── google_maps.py  # Google Maps API integration
│       ├── ai_service.py   # Anthropic Claude integration
│       ├── push_notification.py  # FCM push notifications
│       └── scheduler.py    # Background traffic polling
```

## API Endpoints

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/me/routes` - Get user's routes
- `GET /api/v1/users/me/notifications` - Get user's notifications

### Routes
- `GET /api/v1/routes/` - List all routes
- `POST /api/v1/routes/` - Create route
- `GET /api/v1/routes/{id}` - Get route details
- `PATCH /api/v1/routes/{id}` - Update route
- `DELETE /api/v1/routes/{id}` - Delete route
- `GET /api/v1/routes/{id}/traffic-history` - Get traffic history

### Notifications
- `GET /api/v1/notifications/` - List notifications
- `GET /api/v1/notifications/unread` - Get unread notifications

## Development Tips

### Running Tests

```bash
pytest
```

### Database Migrations

For schema changes, use Alembic:

```bash
alembic init alembic
# Configure alembic.ini and env.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Monitoring API Costs

Set up budget alerts in Google Cloud Billing to monitor Maps API usage. The Routes API is billed per request, so frequent polling can add up quickly.

### Optimizing Polling Frequency

Adjust `POLL_INTERVAL_MINUTES` in `.env` based on your needs:
- Lower = more responsive alerts but higher API costs
- Higher = lower costs but potentially delayed alerts

Recommended: Start with 5-10 minutes during commute hours only.
