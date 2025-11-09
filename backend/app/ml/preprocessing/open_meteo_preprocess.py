"""
Data preprocessing for Open-Meteo data using pvlib.
Based on surya_drishti_lite data_preprocess.py
"""
import pandas as pd
import numpy as np
from pathlib import Path
import pvlib
from dateutil import parser as dateutil_parser
import pytz
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def parse_time_series(s: pd.Series) -> pd.Series:
    """Parse timestamps robustly, return UTC tz-aware datetimes."""
    # Attempt fast vectorized parse
    times = pd.to_datetime(s, errors="coerce", utc=True)
    if times.isna().any():
        # Fallback elementwise
        def try_parse(x):
            if pd.isna(x):
                return pd.NaT
            try:
                return pd.to_datetime(x, utc=True)
            except Exception:
                try:
                    dt = dateutil_parser.parse(str(x))
                    if dt.tzinfo is None:
                        tz = pytz.timezone("Asia/Kolkata")
                        dt = tz.localize(dt)
                    return dt.astimezone(pytz.UTC)
                except Exception:
                    return pd.NaT
        times = s.apply(try_parse)
        times = pd.to_datetime(times, utc=True, errors="coerce")
    return times


def preprocess_open_meteo_data(
    df: pd.DataFrame,
    lat: float,
    lon: float,
    target_horizon_hours: int = 24
) -> pd.DataFrame:
    """
    Preprocess Open-Meteo data for model training/prediction.
    
    Args:
        df: DataFrame with Open-Meteo hourly data
        lat: Latitude
        lon: Longitude
        target_horizon_hours: Hours ahead to predict (default 24)
    
    Returns:
        Preprocessed DataFrame with features and target
    """
    df = df.copy()
    
    # Drop duplicate time-like columns if present
    dup_time_cols = [c for c in df.columns if c.lower().startswith("time") and c not in ("time",)]
    if dup_time_cols:
        logger.info(f"Dropping duplicate time-like columns: {dup_time_cols}")
        df = df.drop(columns=dup_time_cols)
    
    # Robust time parsing -> UTC-aware
    if "time" not in df.columns:
        raise ValueError("CSV missing 'time' column")
    
    logger.info("Parsing 'time' column (robust)...")
    df["time"] = parse_time_series(df["time"])
    df = df.dropna(subset=["time"]).copy()
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df = df.sort_values("time").reset_index(drop=True)
    
    # time_local in IST
    IST = pytz.timezone("Asia/Kolkata")
    df["time_local"] = df["time"].dt.tz_convert(IST)
    
    # Keep the common columns we expect (only those that exist)
    candidate_keep = [
        "shortwave_radiation", "direct_radiation", "diffuse_radiation",
        "cloud_cover", "temperature_2m", "relative_humidity_2m",
        "dew_point_2m", "pressure_msl", "wind_speed_10m"
    ]
    avail = [c for c in candidate_keep if c in df.columns]
    # Ensure we have time and time_local, then add available columns
    base_cols = ["time", "time_local"]
    df = df[base_cols + avail].copy()
    
    # Normalize / units: shortwave_radiation may be in J/m^2 (hourly) or W/m^2
    if "shortwave_radiation" in df.columns:
        max_sr = pd.to_numeric(df["shortwave_radiation"], errors="coerce").max()
        if pd.notna(max_sr) and max_sr > 2000:  # very likely J/m2 -> convert
            logger.info("Converting 'shortwave_radiation' J/m² → W/m² by dividing by 3600")
            df["shortwave_radiation"] = pd.to_numeric(df["shortwave_radiation"], errors="coerce") / 3600.0
        else:
            df["shortwave_radiation"] = pd.to_numeric(df["shortwave_radiation"], errors="coerce").fillna(0.0)
    else:
        df["shortwave_radiation"] = 0.0
    
    logger.info(f"shortwave_radiation range: {df['shortwave_radiation'].min():.2f}–{df['shortwave_radiation'].max():.2f}")
    
    # Create GHI target column (use shortwave_radiation as GHI)
    df["ghi"] = df["shortwave_radiation"].fillna(0.0).astype(float)
    
    # Time features
    df["hour"] = df["time_local"].dt.hour
    df["dayofyear"] = df["time_local"].dt.dayofyear
    df["month"] = df["time_local"].dt.month
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    
    # Solar geometry (pvlib)
    logger.info("Computing solar geometry (pvlib)...")
    try:
        # Ensure time_local is timezone-aware for pvlib
        if df["time_local"].dt.tz is None:
            IST = pytz.timezone("Asia/Kolkata")
            df["time_local"] = df["time_local"].dt.tz_localize(IST)
        
        solpos = pvlib.solarposition.get_solarposition(df["time_local"], lat, lon)
        df["solar_elevation"] = solpos["elevation"].fillna(0).clip(lower=0)
        df["solar_zenith"] = solpos["zenith"].fillna(90).clip(upper=90)
        df["solar_azimuth"] = solpos["azimuth"].fillna(0)
        
        logger.info(f"Solar elevation range: {df['solar_elevation'].min():.1f}° to {df['solar_elevation'].max():.1f}°")
    except Exception as e:
        logger.warning(f"Error computing solar geometry: {e}, using defaults")
        df["solar_elevation"] = 0.0
        df["solar_zenith"] = 90.0
        df["solar_azimuth"] = 0.0
    
    # Clear-sky GHI with multiple models for better accuracy
    logger.info("Computing clear-sky GHI (pvlib ineichen + simplified solis)...")
    time_utc_naive = df["time_local"].dt.tz_convert("UTC").dt.tz_localize(None)
    time_index = pd.DatetimeIndex(time_utc_naive)
    site = pvlib.location.Location(lat, lon, tz="UTC")
    
    # Use Ineichen model (good for general use)
    cs = site.get_clearsky(time_index, model="ineichen")
    df["ghi_clear"] = pd.Series(cs["ghi"].values, index=time_index).reindex(time_index).values
    
    # Also compute DNI and DHI for better feature engineering
    if "dni" in cs.columns:
        df["dni_clear"] = pd.Series(cs["dni"].values, index=time_index).reindex(time_index).values
    if "dhi" in cs.columns:
        df["dhi_clear"] = pd.Series(cs["dhi"].values, index=time_index).reindex(time_index).values
    
    # Clear-sky index (ratio of actual to clear-sky)
    # Only calculate when clear-sky > threshold (avoid division by very small numbers)
    clear_sky_threshold = 10.0  # W/m² threshold
    mask_valid = df["ghi_clear"] > clear_sky_threshold
    df["clearsky_index"] = 0.0
    df.loc[mask_valid, "clearsky_index"] = (
        df.loc[mask_valid, "ghi"] / df.loc[mask_valid, "ghi_clear"]
    ).clip(0, 1.5)  # Reasonable range: 0 to 1.5 (1.0 = clear sky)
    
    # Sky clearness (1 = clear, 0 = overcast)
    df["sky_clearness"] = df["clearsky_index"].clip(0, 1.0)
    
    # Expected GHI based on clear-sky (for comparison)
    df["ghi_expected"] = df["ghi_clear"] * df["sky_clearness"]
    
    # Derived trend features
    if "temperature_2m" in df.columns:
        df["temp_diff"] = df["temperature_2m"].diff().fillna(0.0)
        df["temp_ma_3h"] = df["temperature_2m"].rolling(window=3, min_periods=1).mean().fillna(df["temperature_2m"])
    else:
        df["temp_diff"] = 0.0
        df["temp_ma_3h"] = 25.0  # Default temperature
    
    if "cloud_cover" in df.columns:
        df["cloud_trend"] = df["cloud_cover"].diff().fillna(0.0)
        df["cloud_ma_3h"] = df["cloud_cover"].rolling(window=3, min_periods=1).mean().fillna(df["cloud_cover"])
        # Cloud impact on irradiance (higher cloud = lower irradiance)
        df["cloud_impact"] = (100 - df["cloud_cover"]) / 100.0  # Invert: 0% cloud = 1.0 impact, 100% = 0.0
    else:
        df["cloud_trend"] = 0.0
        df["cloud_ma_3h"] = 0.0
        df["cloud_impact"] = 1.0
    
    # Atmospheric features
    if "pressure_msl" in df.columns:
        df["pressure_norm"] = (df["pressure_msl"] - 1013.25) / 50.0  # Normalize around sea level
    else:
        df["pressure_norm"] = 0.0
    
    if "relative_humidity_2m" in df.columns:
        df["humidity_norm"] = df["relative_humidity_2m"] / 100.0
        # Humidity impact (very high humidity can reduce irradiance)
        df["humidity_impact"] = 1.0 - (df["relative_humidity_2m"] - 50.0).clip(0, 50) / 200.0
    else:
        df["humidity_norm"] = 0.5
        df["humidity_impact"] = 1.0
    
    if "dew_point_2m" in df.columns and "temperature_2m" in df.columns:
        df["dewpoint_spread"] = df["temperature_2m"] - df["dew_point_2m"]  # Higher = drier air
    else:
        df["dewpoint_spread"] = 5.0
    
    # Wind impact (high wind can clear clouds, but also indicates weather systems)
    if "wind_speed_10m" in df.columns:
        df["wind_norm"] = df["wind_speed_10m"] / 20.0  # Normalize
    else:
        df["wind_norm"] = 0.0
    
    # Solar position features (enhanced)
    df["solar_elevation_sin"] = np.sin(np.radians(df["solar_elevation"]))
    df["solar_elevation_cos"] = np.cos(np.radians(df["solar_elevation"]))
    df["is_daytime"] = (df["solar_elevation"] > 0).astype(int)
    
    # Seasonal features
    df["dayofyear_sin"] = np.sin(2 * np.pi * df["dayofyear"] / 365.25)
    df["dayofyear_cos"] = np.cos(2 * np.pi * df["dayofyear"] / 365.25)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)
    
    # Lag features (past known GHI)
    for lag in range(1, 7):
        df[f"ghi_lag_{lag}"] = df["ghi"].shift(lag).ffill().bfill().fillna(0.0)
    
    # Shift by 1 hour (simulate last-known value) - important for preventing data leakage
    radiation_cols = ["shortwave_radiation", "direct_radiation", "diffuse_radiation"]
    available_radiation_cols = [col for col in radiation_cols if col in df.columns]
    
    for col in available_radiation_cols:
        df[col] = df[col].shift(1)
    
    # Drop only rows where *all* shifted radiation values are NaN (start of dataset)
    # Only check columns that actually exist
    if available_radiation_cols:
        mask = df[available_radiation_cols].isna().all(axis=1)
        df = df[~mask].reset_index(drop=True)
    
    # Fill remaining missing values only from the past (never forward-fill!)
    df = df.bfill().fillna(0)
    
    # Create target column (GHI N hours ahead) - only for training data
    if target_horizon_hours > 0:
        df[f"target_{target_horizon_hours}h"] = df["ghi"].shift(-target_horizon_hours)
        # Only drop rows with NaN target if we're creating targets (training mode)
        df = df.dropna(subset=[f"target_{target_horizon_hours}h"])
    
    # Final numeric cleanup
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].replace([np.inf, -np.inf], np.nan).ffill().bfill().fillna(0.0)
    df[num_cols] = df[num_cols].clip(lower=-1e6, upper=1e6)
    
    logger.info(f"Preprocessed dataset with {len(df)} rows")
    return df

