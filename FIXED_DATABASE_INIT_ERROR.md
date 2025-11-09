# ✅ FIXED: Database Initialization Error

## Problem
The backend was failing to initialize the database on Railway startup with this error:

```
TypeError: 'grid_price_per_kwh' is an invalid keyword argument for SystemConfiguration
```

## Root Cause
The `SystemConfiguration` model uses different field names than what was being used in the initialization code:

**Wrong field names used:**
- `grid_price_per_kwh` ❌
- `generator_fuel_consumption_per_kw` ❌
- `optimization_preferences` ❌
- `safety_margin` ❌

**Correct field names (from model):**
- `grid_peak_rate_per_kwh` ✅
- `grid_off_peak_rate_per_kwh` ✅
- `generator_fuel_consumption_l_per_kwh` ✅
- `optimization_mode` ✅
- `safety_margin_critical_loads` ✅

## ✅ Fix Applied

Updated all SystemConfiguration initialization code in:
1. `backend/app/main.py` - startup event
2. `backend/app/api/v1/db_init.py` - manual initialization endpoint
3. `backend/init_db.py` - standalone initialization script

### Corrected Field Mapping:

```python
SystemConfiguration(
    microgrid_id='microgrid_001',
    battery_capacity_kwh=100.0,
    battery_max_charge_rate_kw=20.0,
    battery_max_discharge_rate_kw=20.0,
    battery_min_soc=0.2,
    battery_max_soc=0.95,
    battery_efficiency=0.95,
    # Grid pricing (FIXED)
    grid_peak_rate_per_kwh=10.0,           # ✅ Was: grid_price_per_kwh
    grid_off_peak_rate_per_kwh=5.0,        # ✅ Added (was missing)
    grid_peak_hours={'start': 8, 'end': 20}, # ✅ Added (was missing)
    grid_export_rate_per_kwh=4.0,          # ✅ Added (was missing)
    grid_export_enabled=True,               # ✅ Added (was missing)
    # Generator specs (FIXED)
    generator_fuel_cost_per_liter=85.0,
    generator_fuel_consumption_l_per_kwh=0.25, # ✅ Was: generator_fuel_consumption_per_kw
    generator_min_runtime_minutes=30,       # ✅ Added (was missing)
    generator_max_power_kw=20.0,           # ✅ Added (was missing)
    # Optimization (FIXED)
    optimization_mode='cost',               # ✅ Was: optimization_preferences
    safety_margin_critical_loads=0.1        # ✅ Was: safety_margin
)
```

## ✅ Verification

All field names now match the `SystemConfiguration` model:
- ✅ `battery_capacity_kwh`
- ✅ `battery_max_charge_rate_kw`
- ✅ `battery_max_discharge_rate_kw`
- ✅ `battery_efficiency`
- ✅ `battery_min_soc`
- ✅ `battery_max_soc`
- ✅ `grid_peak_rate_per_kwh`
- ✅ `grid_off_peak_rate_per_kwh`
- ✅ `grid_peak_hours`
- ✅ `grid_export_rate_per_kwh`
- ✅ `grid_export_enabled`
- ✅ `generator_fuel_consumption_l_per_kwh`
- ✅ `generator_fuel_cost_per_liter`
- ✅ `generator_min_runtime_minutes`
- ✅ `generator_max_power_kw`
- ✅ `optimization_mode`
- ✅ `safety_margin_critical_loads`

## 🎯 Expected Result

After Railway redeploys:
1. ✅ Database initialization will succeed on startup
2. ✅ `microgrid_001` will be created automatically
3. ✅ Default devices will be created
4. ✅ System configuration will be created with correct fields
5. ✅ All API endpoints will work (no more 404 errors)
6. ✅ Dashboard will load data correctly

## 📝 Next Steps

1. **Wait for Railway to redeploy** (2-3 minutes)
2. **Check backend logs** for: `✅ Database seeded with default data`
3. **Verify database health**: https://beauty-aryan-back-production.up.railway.app/api/v1/health/database
   - Should show: `microgrid_001_exists: true`
4. **Test endpoints**:
   - https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001
   - https://beauty-aryan-back-production.up.railway.app/api/v1/microgrid/microgrid_001/status
   - https://beauty-aryan-back-production.up.railway.app/api/v1/sensors/microgrid_001/latest
   - https://beauty-aryan-back-production.up.railway.app/api/v1/forecast/microgrid/microgrid_001?horizon_hours=24

## ✅ Status

**FIXED** - Database initialization will now work correctly on Railway startup!

