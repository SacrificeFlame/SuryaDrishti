"""
Open-Meteo API service for fetching historical and forecast weather data.
Based on surya_drishti_lite fetch_open_meteo.py
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class OpenMeteoService:
    """Service for fetching weather data from Open-Meteo API"""
    
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/era5"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self, timezone: str = "Asia/Kolkata"):
        self.timezone = timezone
    
    def fetch_history(
        self, 
        lat: float, 
        lon: float, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        days: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch historical weather data from Open-Meteo archive.
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date in YYYY-MM-DD format (optional if days provided)
            end_date: End date in YYYY-MM-DD format (optional if days provided)
            days: Optional number of days (overrides start_date/end_date if provided)
        
        Returns:
            DataFrame with hourly weather data
        """
        if days is not None:
            # Use yesterday as end date to ensure data is available
            end = datetime.now() - timedelta(days=1)
            start = end - timedelta(days=days)
            # Ensure we don't go too far back (ERA5 archive has limits)
            if start < datetime(2020, 1, 1):
                start = datetime(2020, 1, 1)
            start_date = start.date().isoformat()
            end_date = end.date().isoformat()
        elif start_date is None or end_date is None:
            # Default to 365 days if neither days nor dates provided
            # Use yesterday as end date to ensure data is available
            end = datetime.now() - timedelta(days=1)
            start = end - timedelta(days=365)
            if start < datetime(2020, 1, 1):
                start = datetime(2020, 1, 1)
            start_date = start.date().isoformat()
            end_date = end.date().isoformat()
        else:
            # Validate provided dates - ensure end_date is not in the future
            if isinstance(end_date, str):
                # Parse string date
                try:
                    end_dt = datetime.fromisoformat(end_date)
                    if isinstance(end_dt, pd.Timestamp):
                        end_date_obj = end_dt.date()
                    else:
                        end_date_obj = end_dt.date()
                except:
                    # Try parsing as date string
                    from dateutil import parser
                    end_dt = parser.parse(end_date)
                    end_date_obj = end_dt.date()
            elif isinstance(end_date, pd.Timestamp):
                end_date_obj = end_date.date()
            elif hasattr(end_date, 'date'):
                end_date_obj = end_date.date()
            else:
                # Assume it's already a date object
                end_date_obj = end_date
            
            # Ensure end_date is not in the future (use yesterday if needed)
            today = datetime.now().date()
            if end_date_obj >= today:
                end_dt = datetime.now() - timedelta(days=1)
                end_date = end_dt.date().isoformat()
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "shortwave_radiation,direct_radiation,diffuse_radiation,cloud_cover,temperature_2m,relative_humidity_2m,dew_point_2m,pressure_msl,wind_speed_10m",
            "timezone": self.timezone
        }
        
        try:
            logger.info(f"Fetching historical data for {lat},{lon} from {start_date} to {end_date}")
            r = requests.get(self.ARCHIVE_URL, params=params, timeout=15)  # Reduced from 60s to 15s
            r.raise_for_status()
            data = r.json()["hourly"]
            df = pd.DataFrame(data)
            df["time"] = pd.to_datetime(df["time"])
            logger.info(f"Fetched {len(df)} historical records")
            return df
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching historical data: {e}")
            if r.status_code == 400:
                logger.error(f"Request URL: {r.url}")
                logger.error(f"Response: {r.text[:500]}")
                raise ValueError(f"Invalid date range or parameters. API returned: {r.text[:200]}")
            raise
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    def fetch_forecast(
        self, 
        lat: float, 
        lon: float, 
        hours: int = 24
    ) -> pd.DataFrame:
        """
        Fetch forecast data from Open-Meteo.
        
        Args:
            lat: Latitude
            lon: Longitude
            hours: Number of hours to forecast (default 24)
        
        Returns:
            DataFrame with hourly forecast data
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "shortwave_radiation,direct_radiation,diffuse_radiation,cloud_cover,temperature_2m,relative_humidity_2m,dew_point_2m,pressure_msl,wind_speed_10m",
            "timezone": self.timezone
        }
        
        try:
            logger.info(f"Fetching forecast data for {lat},{lon} (next {hours} hours)")
            r = requests.get(self.FORECAST_URL, params=params, timeout=10)  # Reduced from 30s to 10s
            r.raise_for_status()
            data = r.json()["hourly"]
            df = pd.DataFrame(data)
            df["time"] = pd.to_datetime(df["time"])
            
            # Filter to future hours only
            # Ensure timezone consistency for comparison
            try:
                import pytz
                tz = pytz.timezone(self.timezone)
                
                # Get current time in the requested timezone
                now_ts = pd.Timestamp.now(tz=tz)
                
                # Ensure df["time"] is timezone-aware
                if df["time"].dt.tz is None:
                    df["time"] = df["time"].dt.tz_localize(tz)
                
                # Simple comparison: convert both to same timezone and compare
                # Get timezone from the dataframe (all should have same tz)
                df_tz = df["time"].dt.tz
                if df_tz is not None:
                    # If df has timezone, convert now_ts to that timezone
                    if isinstance(df_tz, pd.Series):
                        # Multiple timezones (unlikely but handle it)
                        df_utc = df["time"].dt.tz_convert('UTC')
                        now_utc = pd.Timestamp.now(tz='UTC')
                        mask = df_utc >= now_utc
                    else:
                        # Single timezone - get it from first element
                        if len(df) > 0:
                            first_tz = df["time"].iloc[0].tz
                            now_in_df_tz = now_ts.tz_convert(first_tz) if first_tz else now_ts
                            mask = df["time"] >= now_in_df_tz
                        else:
                            mask = pd.Series([False] * len(df), index=df.index)
                else:
                    # No timezone, use naive comparison
                    mask = df["time"] >= pd.Timestamp.now()
                
            except Exception as e:
                logger.warning(f"Timezone comparison issue: {e}, using alternative method")
                # Alternative: convert to UTC for comparison
                try:
                    if df["time"].dt.tz is not None:
                        df_utc = df["time"].dt.tz_convert('UTC')
                        now_utc = pd.Timestamp.now(tz='UTC')
                        mask = df_utc >= now_utc
                    else:
                        # Localize to timezone first
                        import pytz
                        tz = pytz.timezone(self.timezone)
                        df["time"] = df["time"].dt.tz_localize(tz)
                        now_ts = pd.Timestamp.now(tz=tz)
                        mask = df["time"] >= now_ts
                except Exception as e2:
                    logger.warning(f"Alternative timezone method also failed: {e2}, using naive comparison")
                    # Last resort: naive comparison
                    if df["time"].dt.tz is not None:
                        df["time"] = df["time"].dt.tz_localize(None)
                    mask = df["time"] >= pd.Timestamp.now()
            
            # Filter to future hours only
            df = df[mask].head(hours).reset_index(drop=True)
            logger.info(f"Fetched {len(df)} forecast records")
            return df
        except Exception as e:
            logger.error(f"Error fetching forecast data: {e}")
            raise
    
    def fetch_combined(
        self, 
        lat: float, 
        lon: float, 
        past_days: int = 365,
        forecast_hours: int = 24
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fetch both historical and forecast data.
        
        Returns:
            Tuple of (historical_df, forecast_df)
        """
        hist_df = self.fetch_history(lat, lon, days=past_days)
        fc_df = self.fetch_forecast(lat, lon, hours=forecast_hours)
        return hist_df, fc_df


