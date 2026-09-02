# RoadPulse — AI-Powered Real-Time Traffic Notification App

## Overview

RoadPulse monitors your saved routes and pushes **real-time, AI-generated traffic alerts** with plain-language notifications and actionable suggestions.

## 🌐 View Demo & Website

Check out our landing page hosted on GitHub Pages: **[yourusername].github.io/roadpulse**

The website includes:
- Interactive demo of the mobile app interface
- Feature showcase
- How it works section
- Download links

## Project Structure

```
/workspace
├── backend/          # Python FastAPI API server
├── mobile/           # React Native (Expo) app
├── web/              # GitHub Pages landing site
│   ├── index.html    # Landing page HTML
│   ├── styles.css    # Page styles
│   └── script.js     # Interactive features
├── docs/             # Documentation & architecture diagrams
└── README.md         # This file
```

## Tech Stack

- **Web**: HTML5, CSS3, JavaScript (GitHub Pages compatible)
- **Mobile**: React Native (Expo)
- **Backend**: Python FastAPI
- **Database**: PostgreSQL + Redis
- **Maps**: Google Maps Platform (Routes API, Roads API, Places API)
- **AI**: Anthropic Claude API
- **Push**: Firebase Cloud Messaging (FCM)

## Getting Started

### Web Landing Page (GitHub Pages)

The landing page is ready to be deployed to GitHub Pages:

1. Push this repository to GitHub
2. Go to Settings > Pages
3. Select the branch you want to deploy from (usually `main`)
4. Set the folder to `/web` (root of the web directory)
5. Your site will be live at `https://yourusername.github.io/roadpulse`

**Alternative**: Copy the contents of the `web/` folder to the root of a GitHub Pages branch (`gh-pages`).

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
## GitHub Pages Deployment

### Option 1: Using GitHub Actions (Recommended)

Create a `.github/workflows/deploy-pages.yml` file:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './web'
      
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Option 2: Manual Deployment

1. Create a `gh-pages` branch:
   ```bash
   git checkout --orphan gh-pages
   git reset --hard
   cp -r web/* .
   git add .
   git commit -m "Deploy landing page to GitHub Pages"
   git push origin gh-pages
   ```

2. In GitHub Settings > Pages, select `gh-pages` branch as source.

## Development Roadmap

- [x] Project setup & documentation
- [x] Landing page for GitHub Pages
- [ ] Phase 1: Auth, Route Saving, Map UI (Weeks 1-4)
- [ ] Phase 2: Traffic Polling Engine (Weeks 5-6)
- [ ] Phase 3: AI Notification Layer (Weeks 7-8)
- [ ] Phase 4: Personalization & Advanced Features (Weeks 9+)

## License

MIT
