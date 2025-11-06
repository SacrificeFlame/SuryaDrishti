#!/usr/bin/env python3
"""
Generate synthetic satellite imagery and training data for SuryaDrishti
"""
import numpy as np
import os
from scipy.ndimage import gaussian_filter
from tqdm import tqdm
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def generate_cloud_pattern(size=(256, 256), num_clouds=5, seed=None):
    """
    Generate synthetic cloud pattern using Perlin-like noise.
    
    Returns:
        cloud_mask: (H, W) array with values 0-3 representing cloud types
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Initialize clear sky
    mask = np.zeros(size, dtype=np.uint8)
    
    # Generate multiple cloud layers
    for _ in range(num_clouds):
        # Random cloud center
        cy = np.random.randint(size[0])
        cx = np.random.randint(size[1])
        
        # Cloud size and type
        cloud_size = np.random.randint(20, 80)
        cloud_type = np.random.randint(1, 4)  # 1=thin, 2=thick, 3=storm
        
        # Create cloud blob
        y, x = np.ogrid[:size[0], :size[1]]
        dist = np.sqrt((y - cy)**2 + (x - cx)**2)
        
        # Gaussian-like falloff
        cloud_blob = np.exp(-(dist**2) / (2 * cloud_size**2))
        cloud_blob = (cloud_blob > 0.3).astype(np.uint8) * cloud_type
        
        # Add to mask (max operation to layer clouds)
        mask = np.maximum(mask, cloud_blob)
    
    # Apply Gaussian blur for smooth edges
    mask_float = gaussian_filter(mask.astype(float), sigma=2)
    mask = np.round(mask_float).astype(np.uint8)
    mask = np.clip(mask, 0, 3)
    
    return mask

def generate_multispectral_image(cloud_mask, size=(256, 256)):
    """
    Generate 6-channel multispectral satellite image.
    Channels: R, G, B, NIR, SWIR, IR
    
    Returns:
        image: (H, W, 6) array
    """
    image = np.zeros((*size, 6), dtype=np.uint8)
    
    # Base sky color (blue)
    image[:, :, 0] = 135  # R
    image[:, :, 1] = 206  # G
    image[:, :, 2] = 235  # B
    
    # NIR (high for clear sky)
    image[:, :, 3] = 200
    
    # SWIR (medium)
    image[:, :, 4] = 150
    
    # IR (thermal - varies with clouds)
    image[:, :, 5] = 180
    
    # Modify based on cloud mask
    for cloud_type in range(1, 4):
        mask = (cloud_mask == cloud_type)
        
        if cloud_type == 1:  # Thin clouds
            image[mask, 0] = 240
            image[mask, 1] = 240
            image[mask, 2] = 245
            image[mask, 3] = 180
            image[mask, 5] = 200
        elif cloud_type == 2:  # Thick clouds
            image[mask, 0] = 220
            image[mask, 1] = 220
            image[mask, 2] = 220
            image[mask, 3] = 140
            image[mask, 5] = 220
        elif cloud_type == 3:  # Storm clouds
            image[mask, 0] = 100
            image[mask, 1] = 100
            image[mask, 2] = 100
            image[mask, 3] = 80
            image[mask, 5] = 240
    
    # Add some noise
    noise = np.random.normal(0, 5, image.shape).astype(np.int16)
    image = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    return image

def generate_irradiance_features(cloud_mask, latitude=28.4595, hour=12):
    """
    Generate features and target for irradiance forecasting.
    
    Returns:
        features: (15,) array
        target: scalar irradiance value
        zenith: solar zenith angle
        opacity: average cloud opacity
    """
    from app.utils.physics import calculate_solar_zenith, calculate_clear_sky_irradiance
    from datetime import datetime
    
    # Calculate solar position
    timestamp = datetime(2024, 6, 15, hour, 0)
    zenith = calculate_solar_zenith(latitude, 77.0, timestamp)
    clear_sky = calculate_clear_sky_irradiance(zenith)
    
    # Cloud statistics
    cloud_coverage = np.mean(cloud_mask > 0)
    avg_opacity = np.mean(cloud_mask) / 3.0  # Normalize to 0-1
    max_opacity = np.max(cloud_mask) / 3.0
    
    # Calculate actual irradiance based on clouds
    attenuation_map = {0: 1.0, 1: 0.7, 2: 0.3, 3: 0.1}
    attenuations = np.array([attenuation_map[val] for val in cloud_mask.flatten()])
    avg_attenuation = np.mean(attenuations)
    actual_irradiance = clear_sky * avg_attenuation
    
    # Build feature vector (15 features)
    features = np.array([
        avg_opacity,              # 0: Average cloud opacity
        cloud_coverage,           # 1: Cloud coverage fraction
        zenith,                   # 2: Solar zenith angle
        clear_sky,                # 3: Clear-sky irradiance
        hour / 24.0,              # 4: Time of day (normalized)
        0.5,                      # 5: Season (0=winter, 1=summer)
        30.0,                     # 6: Temperature (°C)
        45.0,                     # 7: Humidity (%)
        5.0,                      # 8: Wind speed (m/s)
        0.1,                      # 9: Aerosol optical depth
        max_opacity,              # 10: Maximum cloud opacity
        np.std(cloud_mask) / 3.0, # 11: Cloud opacity variance
        latitude / 90.0,          # 12: Latitude (normalized)
        0.0,                      # 13: Cloud motion speed (placeholder)
        0.0,                      # 14: Cloud distance (placeholder)
    ])
    
    return features, actual_irradiance, zenith, avg_opacity

def main():
    """Generate comprehensive training dataset"""
    print("Generating synthetic satellite imagery and training data...")
    
    # Create directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('data/models', exist_ok=True)
    
    # Parameters
    num_samples = 1000
    image_size = (256, 256)
    
    # Storage arrays
    images = []
    masks = []
    features_list = []
    targets = []
    zeniths = []
    opacities = []
    
    print(f"\nGenerating {num_samples} samples...")
    for i in tqdm(range(num_samples)):
        # Generate cloud pattern
        cloud_mask = generate_cloud_pattern(image_size, num_clouds=np.random.randint(3, 8), seed=i)
        
        # Generate multispectral image
        image = generate_multispectral_image(cloud_mask, image_size)
        
        # Generate irradiance features
        hour = 6 + (i % 12)  # Vary time of day (6 AM to 6 PM)
        features, target, zenith, opacity = generate_irradiance_features(cloud_mask, hour=hour)
        
        images.append(image)
        masks.append(cloud_mask)
        features_list.append(features)
        targets.append(target)
        zeniths.append(zenith)
        opacities.append(opacity)
    
    # Convert to arrays
    images = np.array(images)
    masks = np.array(masks)
    features_array = np.array(features_list)
    targets_array = np.array(targets)
    zeniths_array = np.array(zeniths)
    opacities_array = np.array(opacities)
    
    print(f"\nDataset statistics:")
    print(f"  Images shape: {images.shape}")
    print(f"  Masks shape: {masks.shape}")
    print(f"  Features shape: {features_array.shape}")
    print(f"  Targets shape: {targets_array.shape}")
    print(f"  Average irradiance: {np.mean(targets_array):.2f} W/m²")
    
    # Save data
    print("\nSaving data...")
    np.save('data/processed/images.npy', images)
    np.save('data/processed/masks.npy', masks)
    np.savez('data/processed/irradiance_data.npz',
             features=features_array,
             targets=targets_array,
             zenith=zeniths_array,
             opacity=opacities_array)
    
    # Save some samples for inspection
    print("\nSaving sample images...")
    for i in range(min(5, num_samples)):
        np.save(f'data/raw/sample_image_{i}.npy', images[i])
        np.save(f'data/raw/sample_mask_{i}.npy', masks[i])
    
    print("\n✅ Sample data generation complete!")
    print(f"   - {num_samples} training samples created")
    print(f"   - Saved to data/processed/")
    print(f"   - Ready for model training")

if __name__ == "__main__":
    main()


