import torch
import torch.nn as nn
import numpy as np

class MotionLSTM(nn.Module):
    """
    LSTM model for predicting future cloud motion patterns
    """
    def __init__(self, input_size=2, hidden_size=64, num_layers=2, output_size=2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, output_size)
        )
    
    def forward(self, x, hidden=None):
        """
        Args:
            x: (batch, seq_len, input_size) motion history
            hidden: Optional hidden state
            
        Returns:
            output: (batch, output_size) predicted motion
        """
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Use last output
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layer
        prediction = self.fc(last_output)
        
        return prediction, hidden
    
    def predict_sequence(self, initial_sequence, future_steps=4):
        """
        Predict multiple future timesteps
        
        Args:
            initial_sequence: (batch, seq_len, 2) initial motion sequence
            future_steps: Number of future steps to predict
            
        Returns:
            predictions: (batch, future_steps, 2) predicted motions
        """
        self.eval()
        with torch.no_grad():
            predictions = []
            current_sequence = initial_sequence
            hidden = None
            
            for _ in range(future_steps):
                pred, hidden = self.forward(current_sequence, hidden)
                predictions.append(pred)
                
                # Update sequence for next prediction
                current_sequence = torch.cat([
                    current_sequence[:, 1:, :],
                    pred.unsqueeze(1)
                ], dim=1)
            
            predictions = torch.stack(predictions, dim=1)
        
        return predictions

def create_lstm_model():
    """Factory function to create LSTM model"""
    return MotionLSTM(input_size=2, hidden_size=64, num_layers=2, output_size=2)

