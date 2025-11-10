# Frontend Integration Checklist

Quick checklist to verify your integration is complete.

## ✅ Files to Create/Update

### Required Files
- [ ] `frontend/src/types/forecast.ts` - TypeScript type definitions
- [ ] `frontend/src/services/forecastApi.ts` - API service functions
- [ ] `frontend/src/hooks/useForecast.ts` - React hooks
- [ ] `frontend/src/utils/forecastErrorHandler.ts` - Error handling utilities

### Configuration
- [ ] `frontend/.env.local` - Add `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`

## ✅ Integration Steps

### Step 1: Install Dependencies (if needed)
```bash
cd frontend
npm install  # or yarn install
```

### Step 2: Copy Files
All files are already created in the correct locations:
- ✅ `frontend/src/types/forecast.ts`
- ✅ `frontend/src/services/forecastApi.ts`
- ✅ `frontend/src/hooks/useForecast.ts`
- ✅ `frontend/src/utils/forecastErrorHandler.ts`

### Step 3: Update Environment Variables
Add to `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Step 4: Use in Components
```typescript
import { useMicrogridForecast } from '@/hooks/useForecast';

const { forecast, loading, error } = useMicrogridForecast('microgrid_001');
```

## ✅ Testing Checklist

- [ ] Test with valid microgrid ID
- [ ] Test with invalid microgrid ID (should show error)
- [ ] Test loading state (should show spinner)
- [ ] Test error state (should show error message)
- [ ] Test auto-refresh (if enabled)
- [ ] Test manual refetch
- [ ] Verify data displays correctly
- [ ] Check console for errors

## ✅ Common Issues & Fixes

### Issue: "Cannot find module '@/types/forecast'"
**Fix**: Check that `frontend/src/types/forecast.ts` exists and has exports

### Issue: "Cannot find module '@/services/forecastApi'"
**Fix**: Check that `frontend/src/services/forecastApi.ts` exists

### Issue: "Cannot connect to backend"
**Fix**: 
1. Verify backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check CORS settings in backend

### Issue: "Microgrid not found"
**Fix**: 
1. Verify microgrid ID exists in database
2. Check backend logs for errors
3. Test with: `GET /api/v1/microgrid/{id}`

## ✅ Quick Test

Create a test component to verify everything works:

```typescript
// frontend/src/app/test-forecast/page.tsx
'use client';

import { useMicrogridForecast } from '@/hooks/useForecast';

export default function TestForecastPage() {
  const { forecast, loading, error } = useMicrogridForecast('microgrid_001');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!forecast) return <div>No data</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">
        Forecast for {forecast.microgrid.name}
      </h1>
      <div className="space-y-4">
        <div>
          <strong>Total Energy:</strong> {forecast.summary.total_energy_kwh.toFixed(1)} kWh
        </div>
        <div>
          <strong>Mean Power:</strong> {forecast.summary.power_kw.mean.toFixed(1)} kW
        </div>
        <div>
          <strong>Forecast Points:</strong> {forecast.forecast.length}
        </div>
      </div>
    </div>
  );
}
```

Visit: `http://localhost:3000/test-forecast` to test.

## ✅ Integration Complete When:

- [x] All files created
- [x] Types are correct
- [x] Hooks work without errors
- [x] API calls succeed
- [x] Data displays correctly
- [x] Errors are handled gracefully
- [x] Loading states work
- [x] Auto-refresh works (if enabled)

## 📚 Next Steps

1. **Integrate into Dashboard**: Replace existing forecast calls with new hooks
2. **Add Charts**: Use forecast data in chart components
3. **Add Error UI**: Show user-friendly error messages
4. **Add Loading States**: Show spinners during fetch
5. **Add Auto-Refresh**: Enable for real-time updates

---

**Status**: ✅ **Guide is Complete!**

All files are created and ready to use. Follow the checklist above to integrate.






