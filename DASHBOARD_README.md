# SuryaDrishti Dashboard

## Overview

The frontend dashboard is now complete with **sample/mock data** for development and testing. All components are fully functional and styled.

## What's Included

### Components Built

1. **Cloud Movement Map** - Visual representation of cloud coverage and motion vectors
2. **Irradiance Forecast Chart** - P10/P50/P90 quantile predictions with confidence bands
3. **Alerts Panel** - Real-time alert notifications with severity levels
4. **System Status** - Battery SOC, diesel generator status, and power distribution
5. **Performance Metrics** - Key metrics cards (savings, accuracy, uptime, CO2)
6. **Actions Log** - Timeline of automated system actions

### Features

- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Real-time data visualization with mock data
- ✅ Color-coded alerts and status indicators
- ✅ Interactive charts and gauges
- ✅ Professional UI with Tailwind CSS
- ✅ TypeScript type safety

## Running the Dashboard

### Prerequisites

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

Access at: **http://localhost:3000**

The dashboard will automatically redirect to `/dashboard` and display the full interface with sample data.

## Current State

**Status**: ✅ Fully functional with mock data

The dashboard is currently using **mock data** from `src/lib/mockData.ts`. This allows you to:
- View and test all UI components
- Verify the layout and design
- Demonstrate the system without backend connection

## Connecting to Real Backend (Future)

To connect to the real backend API later:

1. **Create API client** (`src/lib/api-client.ts`):
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export async function getForecast(microgridId: string) {
  const res = await fetch(`${API_URL}/api/v1/forecast/current/${microgridId}`);
  return res.json();
}
```

2. **Update dashboard to use real data**:
```typescript
// In dashboard/page.tsx
const [forecastData, setForecastData] = useState(null);

useEffect(() => {
  async function loadData() {
    const data = await getForecast('microgrid_001');
    setForecastData(data);
  }
  loadData();
}, []);
```

3. **Add WebSocket for real-time updates**:
```typescript
// src/hooks/useWebSocket.ts
const ws = new WebSocket('ws://localhost:8001/ws/updates');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update state with real-time data
};
```

## Mock Data Structure

All mock data is centralized in `src/lib/mockData.ts`:

- `mockForecastData` - Forecast response with 5 time points
- `mockSystemStatus` - Battery, diesel, and power distribution
- `mockRecentAlerts` - Sample alerts with different severity levels
- `mockPerformanceMetrics` - KPI metrics
- `mockActionsLog` - Recent automated actions

## Customization

### Changing Mock Data

Edit `frontend/src/lib/mockData.ts` to modify:
- Forecast values
- Alert messages
- System status
- Performance metrics

### Styling

The dashboard uses Tailwind CSS. Modify colors and styles in:
- `tailwind.config.js` - Theme configuration
- Component files - Direct Tailwind classes

### Adding New Components

1. Create component in `src/components/dashboard/`
2. Add to dashboard page: `src/app/dashboard/page.tsx`
3. Update mock data if needed: `src/lib/mockData.ts`

## File Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx          # Main dashboard page
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home (redirects to dashboard)
│   │   └── globals.css            # Global styles
│   ├── components/
│   │   └── dashboard/
│   │       ├── CloudMovementMap.tsx
│   │       ├── IrradianceForecast.tsx
│   │       ├── AlertsPanel.tsx
│   │       ├── SystemStatus.tsx
│   │       ├── PerformanceMetrics.tsx
│   │       └── ActionsLog.tsx
│   ├── lib/
│   │   └── mockData.ts            # Sample data
│   └── types/
│       └── forecast.ts            # TypeScript types
├── package.json
├── tailwind.config.js
├── next.config.js
└── tsconfig.json
```

## Screenshots

When you run the dashboard, you'll see:

1. **Header** - System name, location, and connection status
2. **Performance Metrics Row** - 4 key metric cards
3. **Main Grid**:
   - Left: Irradiance forecast chart with P10/P50/P90 lines
   - Left: Cloud movement map with motion vectors
   - Right: Active alerts panel
   - Right: System status (battery, diesel, power)
4. **Actions Log** - Timeline of recent automated actions
5. **Footer** - Last updated time and system status

## Next Steps

1. **Test the Dashboard**: Run `npm run dev` and explore all components
2. **Customize Mock Data**: Adjust values in `mockData.ts` to test different scenarios
3. **When Ready**: Connect to real backend API (instructions above)

## Notes

- The dashboard is fully responsive and works on mobile devices
- All components are client-side rendered (`'use client'`)
- Mock data is realistic and demonstrates all features
- Ready for integration with real backend when needed

---

**Status**: ✅ Dashboard Complete with Mock Data  
**Last Updated**: November 6, 2025

