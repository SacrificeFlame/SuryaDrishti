import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from .unet import CloudSegmentationModel
import os
from tqdm import tqdm

class CloudDataset(Dataset):
    """Dataset for cloud segmentation training"""
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.samples = []
        
        # Load preprocessed data
        if os.path.exists(os.path.join(data_dir, 'images.npy')):
            self.images = np.load(os.path.join(data_dir, 'images.npy'))
            self.masks = np.load(os.path.join(data_dir, 'masks.npy'))
        else:
            print("No preprocessed data found. Using empty dataset.")
            self.images = np.array([])
            self.masks = np.array([])
    
    def __len__(self):
        return len(self.images) if len(self.images) > 0 else 0
    
    def __getitem__(self, idx):
        image = self.images[idx].astype(np.float32) / 255.0
        mask = self.masks[idx].astype(np.int64)
        
        # Convert to tensors
        image_tensor = torch.from_numpy(image).permute(2, 0, 1)  # (H,W,C) -> (C,H,W)
        mask_tensor = torch.from_numpy(mask)
        
        return image_tensor, mask_tensor

def train_cloud_segmentation(data_dir='data/processed', epochs=50, batch_size=4, lr=1e-3):
    """Train cloud segmentation model"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training on device: {device}")
    
    # Create dataset and dataloader
    dataset = CloudDataset(data_dir)
    
    if len(dataset) == 0:
        print("Warning: Empty dataset. Skipping training.")
        # Create a dummy trained model for testing
        model = CloudSegmentationModel(in_channels=6, num_classes=4)
        os.makedirs('data/models', exist_ok=True)
        torch.save(model.state_dict(), 'data/models/cloud_seg_v1.pth')
        print("Created untrained model for testing purposes.")
        return model
    
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    
    # Initialize model
    model = CloudSegmentationModel(in_channels=6, num_classes=4)
    model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # Training loop
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for images, masks in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            images = images.to(device)
            masks = masks.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, masks)
            
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
    torch.save(model.state_dict(), 'data/models/cloud_seg_v1.pth')
    print("Model saved to data/models/cloud_seg_v1.pth")
    
    return model

if __name__ == "__main__":
    train_cloud_segmentation()


