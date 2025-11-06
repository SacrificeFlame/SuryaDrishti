import numpy as np
from typing import List
import asyncio
from datetime import datetime, timedelta

class SatelliteDataIngester:
    """
    Fetches and preprocesses satellite imagery.
    Mock mode generates synthetic data for testing.
    """
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
    
    async def fetch_latest_image(self, lat: float, lon: float, 
                                  radius_km: float = 50) -> np.ndarray:
        """
        Fetch latest satellite image for given location.
        
        Returns:
            image: (H, W, 6) numpy array with multi-spectral bands
        """
        if self.use_mock:
            return self._generate_mock_image()
        else:
            # In production, fetch from actual satellite API
            raise NotImplementedError("Real satellite data fetching not implemented")
    
    async def fetch_historical_images(self, lat: float, lon: float, 
                                      count: int = 3) -> List[np.ndarray]:
        """
        Fetch recent historical images for motion tracking.
        
        Returns:
            images: List of (H, W, 6) arrays
        """
        images = []
        for i in range(count):
            # Simulate slight temporal variation
            image = self._generate_mock_image(seed=i)
            images.append(image)
            await asyncio.sleep(0.01)  # Simulate API delay
        
        return images
    
    def _generate_mock_image(self, size=(256, 256), seed=None) -> np.ndarray:
        """Generate synthetic satellite imagery"""
        if seed is not None:
            np.random.seed(seed)
        
        # Create base sky image (6 channels)
        image = np.zeros((*size, 6), dtype=np.uint8)
        
        # Base sky color
        image[:, :, 0] = 135  # R
        image[:, :, 1] = 206  # G
        image[:, :, 2] = 235  # B
        image[:, :, 3] = 200  # NIR
        image[:, :, 4] = 150  # SWIR
        image[:, :, 5] = 180  # IR
        
        # Add random clouds
        num_clouds = np.random.randint(2, 6)
        for _ in range(num_clouds):
            cy = np.random.randint(size[0])
            cx = np.random.randint(size[1])
            radius = np.random.randint(20, 60)
            
            y, x = np.ogrid[:size[0], :size[1]]
            dist = np.sqrt((y - cy)**2 + (x - cx)**2)
            
            cloud_mask = dist < radius
            cloud_intensity = 220 + np.random.randint(-20, 20)
            
            image[cloud_mask, 0] = cloud_intensity
            image[cloud_mask, 1] = cloud_intensity
            image[cloud_mask, 2] = cloud_intensity
            image[cloud_mask, 3] = cloud_intensity - 40
            image[cloud_mask, 5] = cloud_intensity + 20
        
        # Add noise
        noise = np.random.normal(0, 5, image.shape).astype(np.int16)
        image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return image


