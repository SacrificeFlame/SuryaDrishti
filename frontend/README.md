# SuryaDrishti - Frontend Dashboard

Next.js 14 dashboard for real-time solar forecasting visualization.

## Setup

### Install Dependencies

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

The dashboard will be available at: http://localhost:3000

## Prerequisites

**Backend must be running!**

Make sure the backend API is running at http://localhost:8000 before starting the frontend:

```bash
cd ../backend
python3 -m uvicorn app.main:app --reload
```

## Features

### 🏠 Home Page (`/`)
- Landing page with project overview
- System status indicators
- Link to dashboard

### 📊 Dashboard (`/dashboard`)
- Real-time forecast visualization
- Interactive charts with Recharts
- Current status cards
- Alerts panel
- System status monitoring
- Forecast details table

### 🔌 Real-time Updates
- WebSocket connection for live alerts
- Auto-refresh forecast every 5 minutes
- System status updates

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **Leaflet** - Maps (ready for integration)

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx           # Home page
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Dashboard
│   │   ├── layout.tsx         # Root layout
│   │   └── globals.css        # Global styles
│   ├── hooks/
│   │   ├── useForecast.ts     # Forecast data fetching
│   │   └── useWebSocket.ts    # WebSocket connection
│   └── types/
│       └── forecast.ts        # TypeScript types
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## API Integration

The dashboard connects to these backend endpoints:

- `GET /api/v1/forecast/current/{microgrid_id}` - Fetch forecast
- `GET /api/v1/microgrid/` - List microgrids
- `WS /ws/updates` - Real-time updates

## Development

### Hot Reload

The development server supports hot reload. Changes to any file will automatically refresh the browser.

### Adding New Components

Create components in `src/components/` and import them in pages.

### Custom Hooks

Custom React hooks are in `src/hooks/` for reusable logic.

## Build for Production

```bash
npm run build
npm start
```

## Troubleshooting

### "Failed to fetch forecast" error

Make sure the backend is running:
```bash
cd ../backend && python3 -m uvicorn app.main:app --reload
```

### WebSocket connection failed

Check that the backend WebSocket endpoint is accessible at `ws://localhost:8000/ws/updates`

### Port 3000 already in use

Change the port:
```bash
PORT=3001 npm run dev
```

## Future Enhancements

- Cloud movement map with Leaflet
- Interactive cloud visualization
- Historical data charts
- Mobile responsive optimizations
- Dark mode support
- Export forecast data
- Multi-microgrid selection

## Related Documentation

- [Main README](../README.md)
- [Backend API Docs](http://localhost:8000/docs)
- [Implementation Summary](../IMPLEMENTATION_SUMMARY.md)

