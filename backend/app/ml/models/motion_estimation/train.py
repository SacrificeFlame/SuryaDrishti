import torch
import torch.nn as nn
import torch.optim as optim
from .lstm_predictor import MotionLSTM
import numpy as np
import os

def train_motion_tracker(epochs=30, lr=1e-3):
    """Train motion tracking LSTM model"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Training motion tracker on device: {device}")
    
    # Create model
    model = MotionLSTM(input_size=2, hidden_size=64, num_layers=2, output_size=2)
    model.to(device)
    
    # For demo purposes, create synthetic training data
    # In production, this would load real motion sequences
    num_samples = 1000
    seq_len = 10
    
    print("Generating synthetic motion data...")
    X_train = torch.randn(num_samples, seq_len, 2) * 0.1  # Small random motions
    y_train = torch.randn(num_samples, 2) * 0.1
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Training loop
    batch_size = 32
    num_batches = num_samples // batch_size
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = start_idx + batch_size
            
            batch_x = X_train[start_idx:end_idx].to(device)
            batch_y = y_train[start_idx:end_idx].to(device)
            
            # Forward pass
            predictions, _ = model(batch_x)
            loss = criterion(predictions, batch_y)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
    
    # Save model
    os.makedirs('data/models', exist_ok=True)
    torch.save(model.state_dict(), 'data/models/motion_tracker_v1.pth')
    print("Model saved to data/models/motion_tracker_v1.pth")
    
    return model

if __name__ == "__main__":
    train_motion_tracker()

