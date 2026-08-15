# RoadPulse - Development & Deployment Guide

## Project Overview

RoadPulse is an AI-powered real-time traffic notification app that monitors your saved routes and sends proactive, intelligent alerts about traffic conditions.

## Quick Start

### Backend (Python FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload
```

### Mobile (React Native + Expo)

```bash
cd mobile
npm install
# Create .env with EXPO_PUBLIC_API_URL=http://your-backend:8000/api/v1
npx expo start
```

## Architecture Summary

```
┌─────────────────┐        ┌──────────────────────┐
│   Mobile App     │◄──────►│   Backend API Server  │
│ (React Native)   │  REST  │ (FastAPI + Python)    │
└─────────────────┘        └──────────┬────────────┘
                                      │
                  ┌───────────────────┼────────────────────┐
                  ▼                   ▼                    ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │ Google Maps       │ │ AI Layer          │ │ Push Service      │
        │ Routes API        │ │ (Claude API)      │ │ (Firebase FCM)    │
        └──────────────────┘ └──────────────────┘ └──────────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │ PostgreSQL        │
        │ + Redis Cache     │
        └──────────────────┘
```

## Core Features Implemented

### Phase 1 (MVP) - Current Status

✅ **Backend**
- User management API (CRUD)
- Route management API (CRUD)
- Traffic monitoring scheduler
- Google Maps Routes API integration
- Anthropic Claude AI alert generation
- Firebase Cloud Messaging integration
- PostgreSQL database models
- Pydantic validation schemas

✅ **Mobile**
- Home screen with route list
- Add route screen
- Location context provider
- API service layer
- Navigation structure

### Phase 2 (Next Steps)

⏳ Scheduled commute windows
⏳ Best-time-to-leave suggestions
⏳ Incident-aware explanations
⏳ Alternate route suggestions
⏳ Map view with route visualization

### Phase 3 (Future)

⏳ Personal pattern learning
⏳ Predictive alerts
⏳ Voice briefings (TTS)
⏳ Community-reported hazards
⏳ Weather correlation

## Required API Keys & Services

### 1. Google Maps Platform
- **Required APIs**: Routes API, Roads API, Places API
- **Setup**: https://console.cloud.google.com/
- **Cost**: ~$5-7 per 1000 requests (Routes API)
- **Tip**: Set budget alerts to avoid surprise charges

### 2. Anthropic (Claude)
- **Required**: API key for Claude model
- **Setup**: https://console.anthropic.com/
- **Cost**: ~$0.003 per 1K tokens (Claude 3 Sonnet)
- **Tip**: Only call AI when delay exceeds threshold

### 3. Firebase
- **Required**: Firebase project + service account
- **Setup**: https://console.firebase.google.com/
- **Cost**: Free tier generous for push notifications
- **Services**: Authentication, Cloud Messaging

### 4. PostgreSQL
- **Version**: 12+
- **Hosting**: Local, AWS RDS, Supabase, etc.
- **Cost**: Free tier available on most platforms

### 5. Redis
- **Version**: 6+
- **Purpose**: Caching, session storage
- **Hosting**: Local, Redis Cloud, AWS ElastiCache

## Environment Variables

### Backend (.env)
```env
GOOGLE_MAPS_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/roadpulse
REDIS_URL=redis://localhost:6379
FIREBASE_CREDENTIALS_PATH=./firebase_credentials.json
FIREBASE_PROJECT_ID=your-project-id
PORT=8000
POLL_INTERVAL_MINUTES=5
```

### Mobile (.env)
```env
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
EXPO_PUBLIC_FIREBASE_CONFIG={"apiKey":"..."}
```

## Testing Checklist

### Backend Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Test specific module
pytest app/services/test_google_maps.py
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Create user
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","firebase_uid":"test-123"}'

# List routes
curl "http://localhost:8000/api/v1/routes/?firebase_uid=test-123"
```

### Mobile Testing
```bash
# Run on iOS simulator
npx expo run:ios

# Run on Android emulator
npx expo run:android

# Build for production
eas build --platform ios
```

## Deployment Options

### Option 1: Render/Railway (Easiest)
```yaml
# render.yaml
services:
  - type: web
    name: roadpulse-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GOOGLE_MAPS_API_KEY
      - key: ANTHROPIC_API_KEY
      - key: DATABASE_URL
```

### Option 2: Docker + AWS ECS
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 3: Serverless (AWS Lambda)
- Use Mangum adapter for FastAPI
- Deploy with Serverless Framework or SAM
- Good for low-traffic MVP

## Cost Optimization Strategies

1. **Smart Polling**
   - Only poll during active commute windows
   - Increase interval when no significant changes
   - Skip polling on weekends if not configured

2. **AI Caching**
   - Cache AI-generated messages for similar conditions
   - Only regenerate when delay changes by >2 minutes
   - Use fallback templates when AI fails

3. **Database Optimization**
   - Archive old traffic checks (>30 days)
   - Use Redis for frequently accessed data
   - Index on `route_id` and `checked_at`

4. **Google Maps Budget**
   - Set daily/monthly budget alerts
   - Use free tier efficiently ($200 monthly credit)
   - Consider batch requests where possible

## Monitoring & Logging

### Recommended Tools
- **Logging**: Structured logging with JSON format
- **Metrics**: Prometheus + Grafana
- **Error Tracking**: Sentry
- **Uptime**: UptimeRobot or Pingdom

### Key Metrics to Track
- API response times
- Google Maps API call count
- AI service latency
- Notification delivery rate
- Active users/routes

## Security Considerations

1. **Authentication**
   - Use Firebase Auth JWT tokens
   - Validate tokens on every request
   - Implement token refresh flow

2. **API Key Protection**
   - Never expose keys in mobile app
   - Use environment variables
   - Rotate keys periodically

3. **Rate Limiting**
   - Implement per-user rate limits
   - Use Redis for distributed rate limiting
   - Return 429 status when exceeded

4. **Data Privacy**
   - Encrypt sensitive data at rest
   - Use HTTPS everywhere
   - Implement data retention policies

## Troubleshooting

### Common Issues

**"Google Maps API error: PERMISSION_DENIED"**
- Check API key restrictions
- Verify billing is enabled
- Ensure Routes API is enabled

**"Failed to connect to PostgreSQL"**
- Verify DATABASE_URL format
- Check database server is running
- Ensure network access allowed

**"Firebase initialization failed"**
- Verify credentials file path
- Check service account has correct permissions
- Ensure FIREBASE_PROJECT_ID matches

**"Scheduler not running"**
- Check APScheduler logs
- Verify async compatibility
- Ensure event loop is running

## Next Development Steps

1. **Complete Mobile UI**
   - [ ] Map view with route visualization
   - [ ] Route detail screen with traffic history
   - [ ] Settings screen for notification preferences
   - [ ] Firebase Auth integration

2. **Enhance Backend**
   - [ ] Real-time WebSocket updates
   - [ ] Batch traffic checking optimization
   - [ ] Historical pattern analysis
   - [ ] A/B testing framework for AI prompts

3. **Testing & QA**
   - [ ] Unit tests for services
   - [ ] Integration tests for API
   - [ ] E2E tests for mobile flows
   - [ ] Load testing for scheduler

4. **Production Readiness**
   - [ ] CI/CD pipeline
   - [ ] Staging environment
   - [ ] Monitoring dashboard
   - [ ] On-call rotation setup

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/roadpulse/issues
- Email: support@roadpulse.app (placeholder)

---

Built with ❤️ using FastAPI, React Native, Google Maps, and Claude AI
