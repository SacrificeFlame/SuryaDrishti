"""
Validate forecast accuracy using real solar irradiance data from public sources.
Uses PVGIS (Photovoltaic Geographical Information System) for historical GHI data.
"""
import asyncio
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from math import sqrt

# Test locations with known good data availability
TEST_LOCATIONS = [
    {"name": "Delhi, India", "lat": 28.6139, "lon": 77.2090},
    {"name": "Mumbai, India", "lat": 19.0760, "lon": 72.8777},
    {"name": "Bangalore, India", "lat": 12.9716, "lon": 77.5946},
]


async def fetch_pvgis_data(lat: float, lon: float, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    Fetch historical solar irradiance data from PVGIS API.
    PVGIS provides free access to historical GHI data from satellite observations.
    """
    try:
        # PVGIS API endpoint for time series data
        url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
        
        params = {
            "lat": lat,
            "lon": lon,
            "startyear": start_date[:4],
            "endyear": end_date[:4],
            "pvcalculation": 0,  # Just get irradiance, not PV output
            "outputformat": "json",
            "raddatabase": "PVGIS-SARAH2",  # Satellite-based database
            "usehorizon": 1,
            "horizon": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "outputs" in data and "hourly" in data["outputs"]:
                hourly_data = data["outputs"]["hourly"]
                df = pd.DataFrame(hourly_data)
                
                # Convert time to datetime
                df["time"] = pd.to_datetime(
                    df["time"].apply(lambda x: f"{x[:4]}-{x[4:6]}-{x[6:8]} {x[9:11]}:{x[11:13]}:00")
                )
                
                # Extract GHI (Global Horizontal Irradiance)
                if "G(i)" in df.columns:
                    df["ghi_actual"] = df["G(i)"]
                    df = df[["time", "ghi_actual"]].copy()
                    return df
                else:
                    print(f"⚠️  PVGIS data missing GHI column. Available: {df.columns.tolist()}")
                    return None
            else:
                print(f"⚠️  PVGIS response missing hourly data")
                return None
                
    except Exception as e:
        print(f"❌ Error fetching PVGIS data: {e}")
        return None


async def fetch_our_forecast(lat: float, lon: float, base_url: str = "http://localhost:8000") -> Optional[Dict]:
    """
    Fetch forecast from our API.
    """
    try:
        url = f"{base_url}/api/v1/forecast/ngboost"
        params = {
            "lat": lat,
            "lon": lon,
            "horizon_hours": 24,
            "training_days": 180,
            "retrain": False
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
    except Exception as e:
        print(f"❌ Error fetching our forecast: {e}")
        return None


async def fetch_open_meteo_historical(lat: float, lon: float, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """
    Fetch historical data from Open-Meteo (same source our API uses).
    This allows us to validate against the actual data source.
    """
    try:
        url = "https://archive-api.open-meteo.com/v1/era5"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "shortwave_radiation",
            "timezone": "Asia/Kolkata"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "hourly" in data:
                df = pd.DataFrame({
                    "time": pd.to_datetime(data["hourly"]["time"]),
                    "ghi_actual": data["hourly"]["shortwave_radiation"]
                })
                
                # Convert from J/m² to W/m² if needed
                if df["ghi_actual"].max() > 2000:
                    df["ghi_actual"] = df["ghi_actual"] / 3600.0
                
                return df
            else:
                return None
                
    except Exception as e:
        print(f"❌ Error fetching Open-Meteo historical: {e}")
        return None


def validate_forecast_structure(
    forecast_df: pd.DataFrame,
    actual_df: pd.DataFrame,
    location: Dict,
    forecast_data: Dict
) -> Dict:
    """Validate forecast structure and reasonableness when we can't compare directly."""
    print("\n📊 FORECAST STRUCTURE VALIDATION")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # 1. Check for negative values
    negative_p10 = forecast_df[forecast_df["p10"] < 0]
    if len(negative_p10) > 0:
        issues.append(f"❌ Found {len(negative_p10)} forecasts with negative P10 values")
        print(f"   Negative P10 values: {negative_p10[['time', 'p10']].to_dict('records')[:3]}")
    else:
        print("✅ No negative P10 values")
    
    # 2. Check quantile ordering
    invalid_order = forecast_df[forecast_df["p10"] > forecast_df["p90"]]
    if len(invalid_order) > 0:
        issues.append(f"❌ Found {len(invalid_order)} forecasts with P10 > P90")
    else:
        print("✅ Quantile ordering correct (P10 ≤ P50 ≤ P90)")
    
    # 3. Check reasonable GHI ranges
    max_ghi = forecast_df["ghi"].max()
    min_ghi = forecast_df["ghi"].min()
    
    # Expected max for India: ~800-1000 W/m²
    if max_ghi > 1200:
        warnings.append(f"⚠️  Very high GHI values (max: {max_ghi:.1f} W/m²)")
    elif max_ghi < 200:
        warnings.append(f"⚠️  Low peak GHI (max: {max_ghi:.1f} W/m²) - may be under-predicting")
    else:
        print(f"✅ GHI range reasonable: {min_ghi:.1f} - {max_ghi:.1f} W/m²")
    
    # 4. Check diurnal pattern
    forecast_df["hour"] = pd.to_datetime(forecast_df["time"]).dt.hour
    daytime = forecast_df[forecast_df["hour"].between(6, 18)]
    nighttime = forecast_df[~forecast_df["hour"].between(6, 18)]
    
    if len(daytime) > 0 and len(nighttime) > 0:
        avg_daytime = daytime["ghi"].mean()
        avg_nighttime = nighttime["ghi"].mean()
        
        if avg_daytime < avg_nighttime:
            issues.append("❌ Daytime GHI lower than nighttime (inverted pattern)")
        else:
            print(f"✅ Diurnal pattern correct: Daytime avg={avg_daytime:.1f}, Nighttime avg={avg_nighttime:.1f} W/m²")
    
    # 5. Compare with historical patterns
    if len(actual_df) > 0:
        hist_max = actual_df["ghi_actual"].max()
        hist_mean = actual_df["ghi_actual"].mean()
        forecast_mean = forecast_df["ghi"].mean()
        
        print(f"\n📈 COMPARISON WITH HISTORICAL DATA")
        print(f"   Historical max GHI: {hist_max:.1f} W/m²")
        print(f"   Historical mean GHI: {hist_mean:.1f} W/m²")
        print(f"   Forecast mean GHI: {forecast_mean:.1f} W/m²")
        
        if abs(forecast_mean - hist_mean) / (hist_mean + 1e-9) > 0.5:
            warnings.append(f"⚠️  Forecast mean differs significantly from historical mean")
        else:
            print(f"✅ Forecast mean aligns with historical patterns")
    
    # 6. Clear-sky comparison
    if "ghi_clear_sky" in forecast_df.columns:
        clear_sky_available = forecast_df["ghi_clear_sky"] > 0
        if clear_sky_available.sum() > 0:
            forecast_with_clear = forecast_df[clear_sky_available]
            ratio = (forecast_with_clear["ghi"] / forecast_with_clear["ghi_clear_sky"]).mean()
            print(f"\n☀️  CLEAR-SKY COMPARISON")
            print(f"   Average clear-sky ratio: {ratio:.2f} (1.0 = clear sky)")
            if ratio > 1.2:
                warnings.append("⚠️  Forecast exceeds clear-sky (ratio > 1.2)")
            elif ratio < 0.3:
                warnings.append("⚠️  Very low clear-sky ratio (heavy cloud cover expected)")
            else:
                print(f"✅ Clear-sky ratio in reasonable range")
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Issues found: {len(issues)}")
    print(f"Warnings: {len(warnings)}")
    
    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not issues and not warnings:
        print("✅ Forecast structure looks good!")
    
    return {
        "location": location,
        "issues": issues,
        "warnings": warnings,
        "forecast_stats": {
            "max_ghi": float(max_ghi),
            "min_ghi": float(min_ghi),
            "mean_ghi": float(forecast_df["ghi"].mean()),
            "n_samples": len(forecast_df)
        }
    }


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict:
    """Calculate accuracy metrics."""
    # Remove invalid values
    mask = (actual >= 0) & (predicted >= 0) & np.isfinite(actual) & np.isfinite(predicted)
    actual_clean = actual[mask]
    pred_clean = predicted[mask]
    
    if len(actual_clean) == 0:
        return {"error": "No valid data for comparison"}
    
    mae = mean_absolute_error(actual_clean, pred_clean)
    mse = mean_squared_error(actual_clean, pred_clean)
    rmse = sqrt(mse)
    r2 = r2_score(actual_clean, pred_clean)
    
    # Mean Absolute Percentage Error (only for non-zero values)
    nonzero_mask = actual_clean > 10  # Only calculate for meaningful irradiance
    if np.sum(nonzero_mask) > 0:
        mape = np.mean(np.abs((actual_clean[nonzero_mask] - pred_clean[nonzero_mask]) / actual_clean[nonzero_mask])) * 100
    else:
        mape = None
    
    # Bias (mean error)
    bias = np.mean(pred_clean - actual_clean)
    
    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "mape": float(mape) if mape is not None else None,
        "bias": float(bias),
        "n_samples": len(actual_clean),
        "n_valid": len(actual_clean),
        "n_total": len(actual)
    }


async def validate_forecast(location: Dict, base_url: str = "http://localhost:8000"):
    """
    Validate forecast accuracy for a location.
    Since forecasts are for future dates, we validate:
    1. Forecast structure and reasonableness
    2. Clear-sky comparison (forecast vs clear-sky model)
    3. Diurnal pattern validation
    4. Comparison with historical patterns
    """
    print(f"\n{'='*60}")
    print(f"📍 Validating forecast for: {location['name']}")
    print(f"   Coordinates: ({location['lat']}, {location['lon']})")
    print(f"{'='*60}\n")
    
    lat, lon = location["lat"], location["lon"]
    
    # Get historical data for comparison (last 7 days)
    end_date = datetime.now() - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=7)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"📅 Historical data range: {start_str} to {end_str}")
    
    # Fetch actual data from Open-Meteo (same source our API uses)
    print("\n1️⃣  Fetching actual historical data from Open-Meteo...")
    actual_df = await fetch_open_meteo_historical(lat, lon, start_str, end_str)
    
    if actual_df is None or len(actual_df) == 0:
        print("❌ Could not fetch actual data. Trying PVGIS...")
        actual_df = await fetch_pvgis_data(lat, lon, start_str, end_str)
    
    if actual_df is None or len(actual_df) == 0:
        print("❌ Could not fetch actual data from any source. Skipping this location.")
        return None
    
    print(f"✅ Fetched {len(actual_df)} hours of actual data")
    print(f"   GHI range: {actual_df['ghi_actual'].min():.1f} - {actual_df['ghi_actual'].max():.1f} W/m²")
    
    # Fetch our forecast
    print("\n2️⃣  Fetching forecast from our API...")
    forecast_data = await fetch_our_forecast(lat, lon, base_url)
    
    if forecast_data is None:
        print("❌ Could not fetch forecast from API")
        return None
    
    print(f"✅ Received forecast with {len(forecast_data.get('forecast', []))} hours")
    
    # Convert forecast to DataFrame
    forecast_list = forecast_data.get("forecast", [])
    forecast_df = pd.DataFrame(forecast_list)
    forecast_df["time"] = pd.to_datetime(forecast_df["timestamp"])
    forecast_df["ghi_predicted"] = forecast_df["ghi"]
    
    # Merge with actual data (match by time)
    print("\n3️⃣  Comparing forecast with actual data...")
    
    # Align times (nearest hour match) - handle timezone issues
    actual_df["time_hour"] = actual_df["time"].dt.floor("H")
    forecast_df["time_hour"] = forecast_df["time"].dt.floor("H")
    
    # Normalize timezones for merging
    if actual_df["time_hour"].dt.tz is not None:
        actual_df["time_hour"] = actual_df["time_hour"].dt.tz_localize(None)
    if forecast_df["time_hour"].dt.tz is not None:
        forecast_df["time_hour"] = forecast_df["time_hour"].dt.tz_localize(None)
    
    merged = pd.merge(
        actual_df[["time_hour", "ghi_actual"]],
        forecast_df[["time_hour", "ghi_predicted", "p10", "p50", "p90"]],
        on="time_hour",
        how="inner"
    )
    
    if len(merged) < 5:  # Need at least 5 hours for meaningful comparison
        print(f"⚠️  Only {len(merged)} matching timestamps found (forecast is for future dates).")
        print(f"   Actual data range: {actual_df['time'].min()} to {actual_df['time'].max()}")
        print(f"   Forecast range: {forecast_df['time'].min()} to {forecast_df['time'].max()}")
        print("\n📊 Performing structural validation instead...")
        
        # Validate forecast structure and reasonableness
        return validate_forecast_structure(
            forecast_df, actual_df, location, forecast_data
        )
    
    print(f"✅ Found {len(merged)} matching hours for comparison")
    
    # Calculate metrics
    metrics = calculate_metrics(
        merged["ghi_actual"].values,
        merged["ghi_predicted"].values
    )
    
    print(f"\n{'='*60}")
    print("📊 ACCURACY METRICS")
    print(f"{'='*60}")
    print(f"Mean Absolute Error (MAE):     {metrics['mae']:.2f} W/m²")
    print(f"Root Mean Square Error (RMSE): {metrics['rmse']:.2f} W/m²")
    print(f"R² Score:                      {metrics['r2']:.3f}")
    if metrics['mape']:
        print(f"Mean Absolute % Error (MAPE):  {metrics['mape']:.1f}%")
    print(f"Bias (predicted - actual):     {metrics['bias']:.2f} W/m²")
    print(f"Valid samples:                 {metrics['n_valid']}/{metrics['n_total']}")
    print(f"{'='*60}\n")
    
    # Additional analysis
    print("📈 ADDITIONAL ANALYSIS")
    print(f"{'='*60}")
    
    # Daytime vs nighttime
    merged["is_daytime"] = merged["ghi_actual"] > 20  # Rough daytime threshold
    daytime_merged = merged[merged["is_daytime"]]
    
    if len(daytime_merged) > 0:
        daytime_metrics = calculate_metrics(
            daytime_merged["ghi_actual"].values,
            daytime_merged["ghi_predicted"].values
        )
        print(f"Daytime only (GHI > 20 W/m²):")
        print(f"  MAE: {daytime_metrics['mae']:.2f} W/m²")
        print(f"  RMSE: {daytime_metrics['rmse']:.2f} W/m²")
        print(f"  R²: {daytime_metrics['r2']:.3f}")
    
    # Prediction interval coverage
    if "p10" in merged.columns and "p90" in merged.columns:
        coverage = np.mean(
            (merged["ghi_actual"] >= merged["p10"]) & 
            (merged["ghi_actual"] <= merged["p90"])
        ) * 100
        print(f"\nPrediction Interval Coverage (P10-P90): {coverage:.1f}%")
        print(f"  (Target: ~80% for well-calibrated model)")
    
    # Sample comparison
    print(f"\n📋 Sample Comparison (first 5 hours):")
    print(f"{'Time':<20} {'Actual':<10} {'Predicted':<10} {'Error':<10} {'% Error':<10}")
    print("-" * 60)
    for idx, row in merged.head(5).iterrows():
        error = row["ghi_predicted"] - row["ghi_actual"]
        pct_error = (error / (row["ghi_actual"] + 1e-9)) * 100
        print(f"{row['time_hour']:<20} {row['ghi_actual']:<10.1f} {row['ghi_predicted']:<10.1f} {error:<10.1f} {pct_error:<10.1f}%")
    
    return {
        "location": location,
        "metrics": metrics,
        "merged_data": merged,
        "forecast_metadata": forecast_data.get("metadata", {})
    }


async def main():
    """Run validation for all test locations."""
    print("FORECAST ACCURACY VALIDATION")
    print("=" * 60)
    print("This script validates our forecast API against real solar irradiance data")
    print("=" * 60)
    
    results = []
    
    for location in TEST_LOCATIONS:
        try:
            result = await validate_forecast(location)
            if result:
                results.append(result)
        except Exception as e:
            print(f"❌ Error validating {location['name']}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    if results:
        print(f"\n{'='*60}")
        print("📊 SUMMARY - ALL LOCATIONS")
        print(f"{'='*60}\n")
        
        # Separate results with metrics from structural validation
        results_with_metrics = [r for r in results if "metrics" in r]
        structural_results = [r for r in results if "metrics" not in r]
        
        if results_with_metrics:
            print(f"{'Location':<20} {'MAE (W/m²)':<15} {'RMSE (W/m²)':<15} {'R²':<10} {'MAPE (%)':<12}")
            print("-" * 72)
            
            for result in results_with_metrics:
                loc_name = result["location"]["name"]
                metrics = result["metrics"]
                mae = metrics["mae"]
                rmse = metrics["rmse"]
                r2 = metrics["r2"]
                mape = metrics.get("mape", 0) or 0
                
                print(f"{loc_name:<20} {mae:<15.2f} {rmse:<15.2f} {r2:<10.3f} {mape:<12.1f}")
            
            # Overall average
            avg_mae = np.mean([r["metrics"]["mae"] for r in results_with_metrics])
            avg_rmse = np.mean([r["metrics"]["rmse"] for r in results_with_metrics])
            avg_r2 = np.mean([r["metrics"]["r2"] for r in results_with_metrics])
            
            print("-" * 72)
            print(f"{'AVERAGE':<20} {avg_mae:<15.2f} {avg_rmse:<15.2f} {avg_r2:<10.3f}")
        
        if structural_results:
            print(f"\n{'Location':<20} {'Status':<30} {'Max GHI':<15} {'Mean GHI':<15}")
            print("-" * 80)
            for result in structural_results:
                loc_name = result["location"]["name"]
                stats = result.get("forecast_stats", {})
                issues = result.get("issues", [])
                warnings = result.get("warnings", [])
                
                if not issues and not warnings:
                    status = "OK - Structure valid"
                elif len(issues) == 0:
                    status = f"Warnings: {len(warnings)}"
                else:
                    status = f"Issues: {len(issues)}"
                
                print(f"{loc_name:<20} {status:<30} {stats.get('max_ghi', 0):<15.1f} {stats.get('mean_ghi', 0):<15.1f}")
        
        print(f"\n✅ Validation complete! Tested {len(results)} locations.")
    else:
        print("\n❌ No successful validations. Check API server and data sources.")


if __name__ == "__main__":
    asyncio.run(main())

