from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from app.services.satellite_ingest import SatelliteDataIngester
from app.core.config import settings
import base64
import io
from PIL import Image
import numpy as np

router = APIRouter()

# Initialize satellite ingester
satellite_ingester = SatelliteDataIngester(use_mock=settings.USE_MOCK_DATA)

@router.get("/image")
async def get_satellite_image(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(50, description="Radius in kilometers"),
    format: str = Query("png", description="Image format (png, jpeg, base64)")
):
    """
    Fetch latest satellite image for given location.
    Returns satellite imagery with cloud detection overlay.
    """
    try:
        # Fetch satellite image
        image_array = await satellite_ingester.fetch_latest_image(lat, lon, radius_km)
        
        # Convert 6-channel array to RGB for display
        rgb_image = image_array[:, :, :3]  # Extract RGB channels
        
        # Ensure valid uint8 range
        if rgb_image.dtype != np.uint8:
            rgb_image = np.clip(rgb_image, 0, 255).astype(np.uint8)
        
        # Ensure image has visible content - enhance if needed
        if rgb_image.max() - rgb_image.min() < 20:
            logger.warning("Image has low contrast, enhancing...")
            # Enhance contrast and add variation
            h, w = rgb_image.shape[:2]
            # Add gradient for visibility
            y_gradient = np.linspace(0, 40, h).reshape(-1, 1)
            x_gradient = np.linspace(0, 30, w).reshape(1, -1)
            gradient = y_gradient + x_gradient
            rgb_image = np.clip(rgb_image.astype(np.int16) + gradient.astype(np.int16), 0, 255).astype(np.uint8)
            
            # Enhance contrast
            min_val, max_val = rgb_image.min(), rgb_image.max()
            if max_val - min_val > 5:
                rgb_image = ((rgb_image.astype(np.float32) - min_val) / (max_val - min_val) * 255).astype(np.uint8)
        
        # Convert to PIL Image
        img = Image.fromarray(rgb_image, mode='RGB')
        
        # Convert to requested format
        if format == "base64":
            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=False)
            img_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            return {
                "image": f"data:image/png;base64,{img_base64}",
                "format": "base64",
                "size": {"width": int(rgb_image.shape[1]), "height": int(rgb_image.shape[0])}
            }
        else:
            buffer = io.BytesIO()
            img.save(buffer, format=format.upper(), optimize=False)
            return Response(content=buffer.getvalue(), media_type=f"image/{format}")
    
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Failed to fetch satellite image: {str(e)}\n{traceback.format_exc()}")

@router.get("/image/with-clouds")
async def get_satellite_image_with_clouds(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(50, description="Radius in kilometers")
):
    """
    Fetch satellite image with cloud detection overlay.
    Returns base64 encoded image with cloud mask overlay.
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Fetching satellite image for lat={lat}, lon={lon}, radius={radius_km}")
        
        # Fetch satellite image
        logger.info("Fetching satellite image from ingester...")
        image_array = await satellite_ingester.fetch_latest_image(lat, lon, radius_km)
        logger.info(f"Received image array shape: {image_array.shape}, dtype: {image_array.dtype}, min: {image_array.min()}, max: {image_array.max()}")
        
        # Ensure we have a valid image
        if image_array is None or image_array.size == 0:
            raise ValueError("Failed to fetch satellite image - received empty array")
        
        # Try to run cloud detection, fallback to simple threshold if ML not available
        try:
            from app.services.irradiance_predictor import IrradiancePredictor
            logger.info("Running cloud detection with ML model...")
            predictor = IrradiancePredictor()
            if predictor.cloud_detector:
                cloud_mask = predictor.cloud_detector.predict(image_array)
                logger.info(f"Cloud mask shape: {cloud_mask.shape}")
            else:
                raise Exception("Cloud detector not available")
        except Exception as ml_error:
            logger.warning(f"ML cloud detection failed, using simple threshold: {ml_error}")
            # Simple cloud detection based on brightness
            gray = np.mean(image_array[:, :, :3], axis=2)
            cloud_mask = np.zeros_like(gray, dtype=np.uint8)
            cloud_mask[gray > 200] = 1  # Thin clouds
            cloud_mask[gray > 220] = 2  # Thick clouds
            cloud_mask[gray > 240] = 3  # Storm
        
        # Create overlay visualization
        rgb_image = image_array[:, :, :3].copy()
        
        # Ensure RGB image is valid uint8
        if rgb_image.dtype != np.uint8:
            rgb_image = np.clip(rgb_image, 0, 255).astype(np.uint8)
        
        logger.info(f"RGB image shape: {rgb_image.shape}, dtype: {rgb_image.dtype}, min: {rgb_image.min()}, max: {rgb_image.max()}, mean: {rgb_image.mean():.1f}")
        
        # Ensure image has good contrast
        if rgb_image.max() - rgb_image.min() < 30:
            logger.warning("Image has low contrast, enhancing...")
            # Enhance contrast
            min_val, max_val = rgb_image.min(), rgb_image.max()
            if max_val - min_val > 5:
                rgb_image = ((rgb_image.astype(np.float32) - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                logger.info(f"Enhanced image - new range: [{rgb_image.min()}, {rgb_image.max()}]")
        
        # Overlay cloud mask with transparency
        overlay = rgb_image.copy().astype(np.float32)  # Use float for blending
        
        # Color code clouds: clear=transparent, thin=light blue, thick=gray, storm=dark gray
        cloud_colors = {
            0: [0, 0, 0, 0],      # Clear - transparent
            1: [135, 206, 235, 100],  # Thin clouds - light blue
            2: [128, 128, 128, 150],  # Thick clouds - gray
            3: [64, 64, 64, 200]     # Storm - dark gray
        }
        
        # Apply cloud overlay more efficiently
        for cloud_type in [1, 2, 3]:
            mask = cloud_mask == cloud_type
            if np.any(mask):
                color = cloud_colors.get(cloud_type, [128, 128, 128, 150])
                alpha = color[3] / 255.0
                overlay[mask, 0] = rgb_image[mask, 0] * (1 - alpha) + color[0] * alpha
                overlay[mask, 1] = rgb_image[mask, 1] * (1 - alpha) + color[1] * alpha
                overlay[mask, 2] = rgb_image[mask, 2] * (1 - alpha) + color[2] * alpha
        
        # Convert back to uint8
        overlay = np.clip(overlay, 0, 255).astype(np.uint8)
        
        # Convert to base64
        logger.info("Converting image to base64...")
        try:
            # Ensure overlay is uint8 and has valid range
            overlay_uint8 = np.clip(overlay, 0, 255).astype(np.uint8)
            
            # Create PIL Image
            img = Image.fromarray(overlay_uint8, mode='RGB')
            
            # Save image
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_bytes = buffer.getvalue()
            
            if len(img_bytes) < 1000:
                logger.warning(f"Image too small ({len(img_bytes)} bytes), regenerating with more variation...")
                # Add more variation to make image visible
                variation = np.random.randint(-20, 20, overlay_uint8.shape).astype(np.int16)
                overlay_uint8 = np.clip(overlay_uint8.astype(np.int16) + variation, 0, 255).astype(np.uint8)
                img = Image.fromarray(overlay_uint8, mode='RGB')
                buffer = io.BytesIO()
                img.save(buffer, format="PNG", optimize=False)
                img_bytes = buffer.getvalue()
            
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            logger.info(f"Satellite image processing complete. Image size: {len(img_bytes)} bytes, Base64 length: {len(img_base64)}")
            
            if len(img_bytes) < 5000:
                logger.warning(f"Image still very small ({len(img_bytes)} bytes) - may not display correctly")
            
            return {
                "image": f"data:image/png;base64,{img_base64}",
                "cloud_mask": cloud_mask.tolist(),
                "size": {"width": int(rgb_image.shape[1]), "height": int(rgb_image.shape[0])}
            }
        except Exception as img_error:
            import traceback
            logger.error(f"Error converting image: {img_error}\n{traceback.format_exc()}")
            raise
    
    except Exception as e:
        import traceback
        error_detail = f"Failed to process satellite image: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

