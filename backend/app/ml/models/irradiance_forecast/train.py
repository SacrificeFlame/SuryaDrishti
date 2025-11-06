import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from .pinn import PhysicsInformedIrradianceModel
import os
from tqdm import tqdm

class IrradianceDataset(Dataset):
    """Dataset for irradiance forecasting"""
    def __init__(self, data_path: str):
        if os.path.exists(data_path):
            data = np.load(data_path)
            self.features = data['features']  # (N, 15)
            self.targets = data['targets']    # (N,) actual irradiance
            self.zenith_angles = data['zenith']  # (N,)
            self.cloud_opacity = data['opacity']  # (N,)
        else:
            print("No preprocessed data found. Using empty dataset.")
            self.features = np.array([])
            self.targets = np.array([])
            self.zenith_angles = np.array([])
            self.cloud_opacity = np.array([])
    
    def __len__(self):
        return len(self.features) if len(self.features) > 0 else 0
    
    def __getitem__(self, idx):
        features = torch.from_numpy(self.features[idx]).float()
        target = torch.from_numpy(np.array([self.targets[idx]])).float()
        zenith = torch.tensor(self.zenith_angles[idx]).float()
        opacity = torch.tensor(self.cloud_opacity[idx]).float()
        
        return features, target, zenith, opacity

def quantile_loss(predictions, targets, quantiles=[0.1, 0.5, 0.9]):
    """
    Pinball loss for quantile regression.
    """
    losses = []
    for i, q in enumerate(quantiles):
        errors = targets - predictions[:, i:i+1]
        losses.append(torch.max((q - 1) * errors, q * errors))
    return torch.mean(torch.stack(losses))

def train_irradiance_model(data_path='data/processed/irradiance_data.npz', 
                           epochs=100, batch_size=64, lr=1e-3):
    """Train irradiance forecasting model"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on device: {device}")
    
    # Load dataset
    dataset = IrradianceDataset(data_path)
    
    if len(dataset) == 0:
        print("Warning: Empty dataset. Creating untrained model.")
        model = PhysicsInformedIrradianceModel(input_features=15, output_quantiles=3)
        os.makedirs('data/models', exist_ok=True)
        torch.save(model.state_dict(), 'data/models/irradiance_v1.pth')
        print("Created untrained model for testing purposes.")
        return model
    
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    
    # Initialize model
    model = PhysicsInformedIrradianceModel(input_features=15, output_quantiles=3)
    model.to(device)
    
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for features, targets, zenith, opacity in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            features = features.to(device)
            targets = targets.to(device)
            zenith = zenith.to(device)
            opacity = opacity.to(device)
            
            # Create physics params
            physics_params = {
                'zenith_angle': zenith,
                'cloud_opacity': opacity
            }
            
            # Forward pass
            predictions = model(features, physics_params)
            loss = quantile_loss(predictions, targets)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        scheduler.step()
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    # Save model
    os.makedirs('data/models', exist_ok=True)
    torch.save(model.state_dict(), 'data/models/irradiance_v1.pth')
    print("Model saved to data/models/irradiance_v1.pth")
    
    return model

if __name__ == "__main__":
    train_irradiance_model()
