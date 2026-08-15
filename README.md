# RoadPulse — AI-Powered Real-Time Traffic Notification App

## Overview

RoadPulse monitors your saved routes and pushes **real-time, AI-generated traffic alerts** with plain-language notifications and actionable suggestions.

## Project Structure

```
/workspace
├── backend/          # Node.js/Python API server
├── mobile/           # React Native (Expo) app
├── docs/             # Documentation & architecture diagrams
└── README.md         # This file
```

## Tech Stack

- **Mobile**: React Native (Expo)
- **Backend**: Python FastAPI
- **Database**: PostgreSQL + Redis
- **Maps**: Google Maps Platform (Routes API, Roads API, Places API)
- **AI**: Anthropic Claude API
- **Push**: Firebase Cloud Messaging (FCM)

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### Mobile Setup

```bash
cd mobile
npm install
npx expo start
```

## Environment Variables

Create `.env` files in both `backend/` and `mobile/` directories:

**Backend `.env`:**
```
GOOGLE_MAPS_API_KEY=your_google_maps_key
ANTHROPIC_API_KEY=your_anthropic_key
DATABASE_URL=postgresql://user:pass@localhost:5432/roadpulse
REDIS_URL=redis://localhost:6379
FIREBASE_CREDENTIALS=path/to/firebase_credentials.json
```

**Mobile `.env`:**
```
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_FIREBASE_CONFIG=your_firebase_config
```

## Development Roadmap

- [x] Project setup & documentation
- [ ] Phase 1: Auth, Route Saving, Map UI (Weeks 1-4)
- [ ] Phase 2: Traffic Polling Engine (Weeks 5-6)
- [ ] Phase 3: AI Notification Layer (Weeks 7-8)
- [ ] Phase 4: Personalization & Advanced Features (Weeks 9+)

## License

MIT