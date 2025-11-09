import numpy as np
from typing import List, Optional, Tuple
import asyncio
from datetime import datetime, timedelta
import aiohttp
import io
from PIL import Image
import cv2
import os
from app.core.config import settings

class SatelliteDataIngester:
    """
    Fetches and preprocesses satellite imagery from various sources.
    Supports NASA Worldview, OpenWeatherMap, and mock data.
    """
    def __init__(self, use_mock: bool = None):
        self.use_mock = use_mock if use_mock is not None else settings.USE_MOCK_DATA
        self.nasa_api_key = settings.NASA_API_KEY or os.getenv('NASA_API_KEY', '')
        self.openweather_api_key = settings.OPENWEATHER_API_KEY or os.getenv('OPENWEATHER_API_KEY', '')
    
    async def fetch_latest_image(self, lat: float, lon: float, 
                                  radius_km: float = 50) -> np.ndarray:
        """
        Fetch latest satellite image for given location.
        
        Returns:
            image: (H, W, 6) numpy array with multi-spectral bands
        """
        print(f"[SATELLITE] Fetching REAL satellite image for location: lat={lat}, lon={lon}, radius={radius_km}km")
        
        if self.use_mock:
            print("[SATELLITE] WARNING: Using mock data (USE_MOCK_DATA=True) - NOT REAL SATELLITE IMAGERY")
            return self._generate_mock_image()
        
        # Try to fetch from real APIs - ONLY use sources that return actual satellite imagery
        # Try NASA Worldview first (returns actual satellite imagery, not cloud maps)
        print("[SATELLITE] Attempting to fetch REAL satellite imagery from NASA Worldview...")
        try:
            image = await self._fetch_nasa_worldview(lat, lon, radius_km)
            if image is not None:
                print("[SATELLITE] ✓ Successfully fetched REAL satellite imagery from NASA Worldview")
                return image
            else:
                print("[SATELLITE] ✗ NASA Worldview returned None")
        except Exception as e:
            print(f"[SATELLITE] ✗ NASA Worldview error: {e}")
            import traceback
            print(traceback.format_exc())
        
        # NOTE: OpenWeatherMap tiles are CLOUD MAPS, not satellite imagery
        # Skip OpenWeatherMap as it doesn't provide actual satellite imagery
        
        # Fallback to mock if APIs fail
        print("[SATELLITE] ✗ WARNING: All REAL satellite API attempts failed!")
        print("[SATELLITE] ✗ Falling back to mock data (NOT REAL SATELLITE IMAGERY)")
        print("[SATELLITE] ✗ Check backend logs above to see why NASA Worldview failed")
        return self._generate_mock_image()
    
    async def _fetch_nasa_worldview(self, lat: float, lon: float, 
                                     radius_km: float) -> Optional[np.ndarray]:
        """
        Fetch satellite imagery from NASA Worldview/Earthdata.
        Uses MODIS Terra/Aqua True Color imagery.
        Note: NASA Worldview WMS doesn't require API key, but we can use NASA API for other endpoints.
        """
        # Calculate bounding box
        bbox = self._calculate_bbox(lat, lon, radius_km)
        
        # NASA Worldview WMS endpoint (public, no API key needed)
        # Try both endpoints - some regions may work better with different endpoints
        base_urls = [
            "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi",
            "https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi",  # Web Mercator projection
        ]
        
        # Use standard resolution
        width = 512
        height = 512
        
        # Try multiple layers - some may not be available for all dates
        layers_to_try = [
            'MODIS_Terra_CorrectedReflectance_TrueColor',
            'MODIS_Aqua_CorrectedReflectance_TrueColor',
            'VIIRS_SNPP_CorrectedReflectance_TrueColor',
        ]
        
        # Try current date and recent dates (data may be delayed)
        dates_to_try = [
            datetime.now().strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        ]
        
        for base_url in base_urls:
            for layer in layers_to_try:
                for date_str in dates_to_try:
                    params = {
                        'SERVICE': 'WMS',
                        'VERSION': '1.1.1',
                        'REQUEST': 'GetMap',
                        'LAYERS': layer,
                        'BBOX': f'{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}',
                        'WIDTH': str(width),
                        'HEIGHT': str(height),
                        'FORMAT': 'image/png',
                        'TIME': date_str,
                    }
                    
                    try:
                        async with aiohttp.ClientSession() as session:
                            headers = {'User-Agent': 'SuryaDrishti/1.0'}
                            async with session.get(base_url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as response:
                                if response.status == 200:
                                    image_data = await response.read()
                                    # Check if we got actual image data (not error message)
                                    if len(image_data) > 1000 and not image_data.startswith(b'<?xml'):
                                        print(f"[SATELLITE] NASA Worldview: Successfully fetched REAL satellite image - {len(image_data)} bytes using {layer} for {date_str} from {base_url}")
                                        # Verify it's a valid PNG/JPEG image
                                        if image_data[:4] == b'\x89PNG' or image_data[:2] == b'\xff\xd8':
                                            print(f"[SATELLITE] ✓ Confirmed valid image format (PNG/JPEG)")
                                            return self._process_satellite_image(image_data, target_size=(256, 256))
                                        else:
                                            print(f"[SATELLITE] ✗ Response is not a valid image format (first bytes: {image_data[:20]})")
                                    else:
                                        print(f"[SATELLITE] NASA Worldview: Got response but appears to be error message (size: {len(image_data)}, starts with: {image_data[:50] if len(image_data) > 0 else 'empty'})")
                                else:
                                    print(f"[SATELLITE] NASA Worldview: HTTP Status {response.status} for {layer} on {date_str} from {base_url}")
                                    # Log response body for debugging
                                    if response.status != 200:
                                        try:
                                            error_text = await response.text()
                                            print(f"[SATELLITE] Error response: {error_text[:200]}")
                                        except:
                                            pass
                    except Exception as e:
                        print(f"[SATELLITE] NASA Worldview fetch error for {layer} on {date_str} from {base_url}: {e}")
                        import traceback
                        print(traceback.format_exc())
                        continue
        
        print("[SATELLITE] ✗ NASA Worldview: All layer/date combinations failed - no REAL satellite imagery available")
        return None
    
    async def _fetch_openweather_satellite(self, lat: float, lon: float,
                                           radius_km: float) -> Optional[np.ndarray]:
        """
        NOTE: OpenWeatherMap tiles are CLOUD MAPS, not actual satellite imagery.
        This function is disabled - we only want REAL satellite imagery.
        """
        print("[SATELLITE] Skipping OpenWeatherMap - it provides cloud maps, not satellite imagery")
        return None
    
    async def _fetch_sentinel_hub(self, lat: float, lon: float,
                                  radius_km: float) -> Optional[np.ndarray]:
        """
        Fetch from Sentinel Hub (requires API key and account).
        Provides high-quality multispectral imagery.
        """
        # Placeholder for Sentinel Hub integration
        # Requires: sentinelhub package and API credentials
        return None
    
    def _calculate_bbox(self, lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
        """Calculate bounding box for satellite imagery"""
        # Approximate conversion: 1 degree ≈ 111 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * np.cos(np.radians(lat)))
        
        return (
            lon - lon_delta,  # min_lon
            lat - lat_delta,  # min_lat
            lon + lon_delta,  # max_lon
            lat + lat_delta   # max_lat
        )
    
    def _calculate_zoom(self, radius_km: float) -> int:
        """Calculate zoom level based on radius"""
        if radius_km <= 5:
            return 12
        elif radius_km <= 20:
            return 11
        elif radius_km <= 50:
            return 10
        else:
            return 9
    
    def _process_satellite_image(self, image_data: bytes, target_size: Tuple[int, int] = (256, 256)) -> np.ndarray:
        """
        Process satellite image to 6-channel format with high quality.
        Converts RGB to multispectral-like format with sharpening.
        """
        # Load image
        img = Image.open(io.BytesIO(image_data))
        img = img.convert('RGB')
        
        # Resize to target size
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        img_array = np.array(img, dtype=np.uint8)
        
        # Convert RGB to 6-channel format (R, G, B, NIR approximation, SWIR approximation, IR approximation)
        # For real satellite data, we approximate missing bands
        h, w = img_array.shape[:2]
        multispectral = np.zeros((h, w, 6), dtype=np.uint8)
        
        # RGB channels - preserve original quality
        multispectral[:, :, 0] = img_array[:, :, 0]  # R
        multispectral[:, :, 1] = img_array[:, :, 1]  # G
        multispectral[:, :, 2] = img_array[:, :, 2]  # B
        
        # Approximate NIR (near-infrared) - clouds are brighter in NIR
        multispectral[:, :, 3] = np.clip(img_array[:, :, 0] * 0.8 + img_array[:, :, 1] * 0.2, 0, 255).astype(np.uint8)
        
        # Approximate SWIR (shortwave infrared)
        multispectral[:, :, 4] = np.clip(img_array[:, :, 0] * 0.6 + img_array[:, :, 2] * 0.4, 0, 255).astype(np.uint8)
        
        # Approximate IR (thermal infrared) - darker for clouds
        multispectral[:, :, 5] = np.clip(255 - img_array.mean(axis=2), 0, 255).astype(np.uint8)
        
        return multispectral
    
    async def fetch_historical_images(self, lat: float, lon: float, 
                                      count: int = 3) -> List[np.ndarray]:
        """
        Fetch recent historical images for motion tracking.
        
        Returns:
            images: List of (H, W, 6) arrays
        """
        images = []
        
        if self.use_mock:
            # Generate mock images with temporal variation
            for i in range(count):
                image = self._generate_mock_image(seed=i)
                images.append(image)
                await asyncio.sleep(0.01)
        else:
            # Fetch historical images from API
            for i in range(count):
                try:
                    # Calculate time for historical image (hours ago)
                    hours_ago = (count - i) * 3  # 3 hours apart
                    image = await self._fetch_historical_image(lat, lon, hours_ago)
                    if image is not None:
                        images.append(image)
                    else:
                        # Fallback to mock if API fails
                        images.append(self._generate_mock_image(seed=i))
                except Exception as e:
                    print(f"Error fetching historical image {i}: {e}")
                    images.append(self._generate_mock_image(seed=i))
                await asyncio.sleep(0.1)  # Rate limiting
        
        return images
    
    async def _fetch_historical_image(self, lat: float, lon: float, hours_ago: int) -> Optional[np.ndarray]:
        """Fetch satellite image from N hours ago"""
        # Similar to fetch_latest_image but with time offset
        # For now, use same approach as latest (APIs may not support historical easily)
        return await self.fetch_latest_image(lat, lon)
    
    def _generate_mock_image(self, size=(256, 256), seed=None) -> np.ndarray:
        """Generate synthetic satellite imagery with visible clouds and terrain"""
        if seed is not None:
            np.random.seed(seed)
        else:
            np.random.seed(int(datetime.now().timestamp()) % 10000)
        
        # Create base sky image (6 channels)
        image = np.zeros((*size, 6), dtype=np.uint8)
        
        # Base sky color - bright blue sky with variation
        base_r, base_g, base_b = 135, 206, 235
        # Add sky gradient (darker at top, brighter at bottom)
        y_gradient = np.linspace(-20, 20, size[0]).reshape(-1, 1)
        image[:, :, 0] = np.clip(base_r + y_gradient, 100, 200).astype(np.uint8)  # R
        image[:, :, 1] = np.clip(base_g + y_gradient, 180, 240).astype(np.uint8)  # G
        image[:, :, 2] = np.clip(base_b + y_gradient, 220, 255).astype(np.uint8)  # B
        image[:, :, 3] = np.clip(200 + y_gradient * 0.5, 150, 250).astype(np.uint8)  # NIR
        image[:, :, 4] = np.clip(150 + y_gradient * 0.3, 100, 200).astype(np.uint8)  # SWIR
        image[:, :, 5] = np.clip(180 + y_gradient * 0.2, 150, 220).astype(np.uint8)  # IR
        
        # Add ground/terrain variation - create visible patterns
        y_coords, x_coords = np.ogrid[:size[0], :size[1]]
        
        # Create terrain patterns (hills, valleys, fields)
        terrain_pattern = (np.sin(x_coords / 25) * np.cos(y_coords / 25) * 40 + 
                          np.sin(x_coords / 15) * np.cos(y_coords / 15) * 20 + 100).astype(np.uint8)
        
        # Add some green/brown terrain colors (fields, forests)
        terrain_mask = terrain_pattern > 120
        image[terrain_mask, 0] = np.clip(image[terrain_mask, 0] * 0.7 + 30, 0, 255).astype(np.uint8)  # More red/brown
        image[terrain_mask, 1] = np.clip(image[terrain_mask, 1] * 0.8 + 40, 0, 255).astype(np.uint8)  # More green
        image[terrain_mask, 2] = np.clip(image[terrain_mask, 2] * 0.6 + 20, 0, 255).astype(np.uint8)  # Less blue
        
        # Add random clouds - make them more visible and realistic
        num_clouds = np.random.randint(4, 10)
        for i in range(num_clouds):
            cy = np.random.randint(size[0] // 5, 4 * size[0] // 5)
            cx = np.random.randint(size[1] // 5, 4 * size[1] // 5)
            radius = np.random.randint(25, 70)
            
            y, x = np.ogrid[:size[0], :size[1]]
            dist = np.sqrt((y - cy)**2 + (x - cx)**2)
            
            # Create soft cloud edges with multiple layers
            cloud_mask = dist < radius
            cloud_fade = np.exp(-(dist / radius) ** 1.5)  # Softer falloff
            
            # Vary cloud brightness (some darker/thicker, some lighter/thinner)
            cloud_brightness = np.random.choice([220, 240, 250])
            cloud_intensity = cloud_brightness + np.random.randint(-15, 15)
            cloud_intensity = np.clip(cloud_intensity, 200, 255)
            
            # Blend clouds with background (make them stand out)
            blend_factor = cloud_fade[cloud_mask]
            image[cloud_mask, 0] = np.clip(
                image[cloud_mask, 0] * (1 - blend_factor * 0.7) + cloud_intensity * blend_factor * 0.7,
                0, 255
            ).astype(np.uint8)
            image[cloud_mask, 1] = np.clip(
                image[cloud_mask, 1] * (1 - blend_factor * 0.7) + cloud_intensity * blend_factor * 0.7,
                0, 255
            ).astype(np.uint8)
            image[cloud_mask, 2] = np.clip(
                image[cloud_mask, 2] * (1 - blend_factor * 0.7) + cloud_intensity * blend_factor * 0.7,
                0, 255
            ).astype(np.uint8)
            
            # Adjust NIR and IR for clouds (clouds are cooler in IR)
            image[cloud_mask, 3] = np.clip(image[cloud_mask, 3] - 40 * blend_factor, 0, 255).astype(np.uint8)
            image[cloud_mask, 5] = np.clip(image[cloud_mask, 5] + 30 * blend_factor, 0, 255).astype(np.uint8)
        
        # Add subtle noise for realism
        noise = np.random.normal(0, 2, image.shape).astype(np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        # Ensure image has good contrast and visibility
        # Normalize to use full dynamic range
        for channel in range(3):  # RGB channels
            channel_data = image[:, :, channel]
            min_val, max_val = channel_data.min(), channel_data.max()
            if max_val - min_val > 10:  # Only normalize if there's variation
                image[:, :, channel] = ((channel_data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        print(f"Generated mock satellite image: shape={image.shape}, range=[{image.min()}, {image.max()}]")
        return image


