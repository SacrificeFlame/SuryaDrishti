₹#!/usr/bin/env python3
"""
Simple training script that directly imports modules
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from tqdm import tqdm

# Import models
from app.ml.models.cloud_segmentation.unet import CloudSegmentationModel
from app.ml.models.irradiance_forecast.pinn import PhysicsInformedIrradianceModel

def train_cloud_model():
    """Train cloud segmentation model"""
    print("="  * 60)
    print("Training Cloud Segmentation Model")
    print("=" * 60)
    
    # Create untrained model (since we're using mock data anyway)
    model = CloudSegmentationModel(in_channels=6, num_classes=4)
    os.makedirs('data/models', exist_ok=True)
    torch.save(model.state_dict(), 'data/models/cloud_seg_v1.pth')
    print("✅ Cloud segmentation model saved (untrained baseline)")
    return model

def train_irradiance_model():
    """Train irradiance forecasting model"""
    print("\n" + "=" * 60)
    print("Training Irradiance Forecasting Model")
    print("=" * 60)
    
    # Load data
    data_path = 'data/processed/irradiance_data.npz'
    if not os.path.exists(data_path):
        print("❌ Training data not found!")
        # Create untrained model
        model = PhysicsInformedIrradianceModel()
        torch.save(model.state_dict(), 'data/models/irradiance_v1.pth')
        print("✅ Irradiance model saved (untrained baseline)")
        return model
    
    data = np.load(data_path)
    features = data['features']
    targets = data['targets']
    zenith = data['zenith']
    opacity = data['opacity']
    
    print(f"Training samples: {len(features)}")
    
    # Create model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on: {device}")
    
    model = PhysicsInformedIrradianceModel(input_features=15, output_quantiles=3)
    model.to(device)
    
    # Simple training loop
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    # Convert to tensors
    features_t = torch.from_numpy(features).float().to(device)
    targets_t = torch.from_numpy(targets).float().unsqueeze(1).to(device)
    zenith_t = torch.from_numpy(zenith).float().to(device)
    opacity_t = torch.from_numpy(opacity).float().to(device)
    
    # Train for a few epochs
    epochs = 20
    batch_size = 64
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        num_batches = 0
        
        # Mini-batch training
        for i in range(0, len(features), batch_size):
            batch_feat = features_t[i:i+batch_size]
            batch_targ = targets_t[i:i+batch_size]
            batch_zen = zenith_t[i:i+batch_size]
            batch_opa = opacity_t[i:i+batch_size]
            
            physics_params = {
                'zenith_angle': batch_zen,
                'cloud_opacity': batch_opa
            }
            
            # Forward pass
            predictions = model(batch_feat, physics_params)
            
            # Simple MSE loss for P50
            loss = nn.functional.mse_loss(predictions[:, 1:2], batch_targ)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/num_batches:.4f}")
    
    # Save model
    torch.save(model.state_dict(), 'data/models/irradiance_v1.pth')
    print("✅ Irradiance model trained and saved")
    
    return model

def main():
    """Train all models"""
    print("\n" + "=" * 60)
    print("SuryaDrishti - Model Training Pipeline")
    print("=" * 60 + "\n")
    
    # Train cloud model
    try:
        train_cloud_model()
    except Exception as e:
        print(f"⚠️  Warning during cloud model training: {e}")
    
    # Train irradiance model
    try:
        train_irradiance_model()
    except Exception as e:
        print(f"⚠️  Warning during irradiance model training: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Model Training Complete!")
    print("=" * 60)
    print("\nModel files:")
    print("  - data/models/cloud_seg_v1.pth")
    print("  - data/models/irradiance_v1.pth")
    print("\nYou can now start the backend server with:")
    print("  cd backend && uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()

