# SEAA Frontend

Modern React + TypeScript dashboard for the Self-Evolving Autonomous Agent.

## Overview

This is a modern, real-time web dashboard for monitoring and controlling SEAA instances. It communicates with the Python backend via:
- **REST API** for status queries
- **WebSocket** for real-time event streaming

## Architecture

```
frontend/                    (This directory - static/built)
├── src/
│   ├── components/         (React components)
│   ├── services/           (API & WebSocket clients)
│   ├── hooks/              (Custom React hooks)
│   ├── types/              (TypeScript type definitions)
│   ├── App.tsx             (Main component)
│   └── main.tsx            (Entry point)
└── dist/                   (Built assets - served by Flask/FastAPI)
```

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

This starts Vite dev server on `http://localhost:3000` with:
- Hot module reloading
- Proxy to `http://localhost:8000/api` for backend
- WebSocket proxy to `ws://localhost:8000/ws`

### Build

```bash
npm run build
```

Outputs minified assets to `dist/` ready for deployment.

### Linting & Type Checking

```bash
npm run lint          # ESLint
npm run type-check    # TypeScript compiler
```

## Components

### StatusCard
Displays instance identity, DNA hash, organ count, and goal progress.

### OrganList
Table of all organs with health status, version, and creation date.

### App
Main component that fetches system status and renders dashboard.

## Services

### API Client (`src/services/api.ts`)
- `getStatus()` - Full system status
- `getIdentity()` - Instance identity
- `getVitals()` - System metrics
- `getOrgans()` - Organ list
- `getGoals()` - Goal status
- `getTimeline()` - Evolution history
- `startGenesis()` / `stopGenesis()` - Control genesis

### WebSocket Client (`src/services/websocket.ts`)
Real-time event streaming with:
- Auto-reconnection with exponential backoff
- Event filtering by type
- Connection state notifications

## Hooks

### useAPI
Generic hook for API calls with loading/error states.

```typescript
const { data, loading, error, refetch } = useAPI(() => apiClient.getStatus())
```

### useWebSocket
Subscribe to real-time events.

```typescript
const { connected, events, clearEvents } = useWebSocket('soma.perception.file_change')
```

## Backend Integration

The frontend expects the Python backend to provide:

### REST Endpoints
```
GET /api/status              - Full system status
GET /api/identity            - Instance identity
GET /api/vitals              - System metrics
GET /api/organs              - Organ list
GET /api/goals               - Goals
GET /api/timeline?limit=20   - Evolution timeline
GET /api/failures            - Failures
POST /api/genesis/start      - Start genesis
POST /api/genesis/stop       - Stop genesis
GET /api/health              - Health check
```

### WebSocket Endpoint
```
WS /ws/events
```

Streams events with format:
```json
{
  "event_type": "soma.perception.file_change",
  "timestamp": "2026-01-31T12:00:00Z",
  "data": { ... }
}
```

## Deployment

The built `dist/` folder should be served by the Python Flask/FastAPI backend:

```python
@app.get('/')
@app.get('/{path:path}')
def serve_frontend(path=''):
    file = Path('frontend/dist') / path
    if not file.is_file():
        file = Path('frontend/dist/index.html')
    return send_file(file)
```

This enables SPA routing with fallback to index.html.

## Styling

Modern dark theme inspired by VS Code and modern dev tools:
- Cyber blue accent: `#00d4ff`
- Health green: `#00c851`
- Warning orange: `#ffb300`
- Error red: `#ff4444`
- Dark background: `#0f1419`, `#1a1a2e`

Responsive design with CSS Grid and mobile support.

## Type Safety

Full end-to-end TypeScript with strict mode enabled:
- Shared types between frontend and API responses
- Type-safe API client
- Component prop types

## Future Enhancements

- [ ] Real-time event log viewer
- [ ] Gene edit interface
- [ ] Organ control (start/stop/restart)
- [ ] Evolution statistics charts
- [ ] Dark/light theme toggle
- [ ] Mobile app (React Native)
- [ ] Multi-instance fleet dashboard
