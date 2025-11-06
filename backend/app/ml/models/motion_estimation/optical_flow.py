import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import List

class CloudMotionTracker:
    """
    Tracks cloud movement using optical flow and LSTM prediction.
    """
    def __init__(self, lstm_model_path: str = None):
        self.flow_method = 'farneback'  # OpenCV optical flow
        self.lstm_predictor = None
        if lstm_model_path:
            try:
                self.lstm_predictor = self.load_lstm_model(lstm_model_path)
            except:
                print("Warning: Could not load LSTM model. Using optical flow only.")
    
    def estimate_motion(self, prev_image: np.ndarray, curr_image: np.ndarray) -> np.ndarray:
        """
        Calculate optical flow between two consecutive satellite images.
        
        Args:
            prev_image: Previous frame (H, W, C) or (H, W)
            curr_image: Current frame (H, W, C) or (H, W)
        
        Returns:
            motion_vectors: (H, W, 2) array with (vx, vy) at each pixel
        """
        # Convert to grayscale if needed
        if len(prev_image.shape) == 3:
            # For multispectral images (6 channels), use only RGB channels (first 3)
            if prev_image.shape[2] > 4:
                prev_rgb = prev_image[:, :, :3]
            else:
                prev_rgb = prev_image
            prev_gray = cv2.cvtColor(prev_rgb, cv2.COLOR_BGR2GRAY)
        else:
            prev_gray = prev_image
            
        if len(curr_image.shape) == 3:
            # For multispectral images (6 channels), use only RGB channels (first 3)
            if curr_image.shape[2] > 4:
                curr_rgb = curr_image[:, :, :3]
            else:
                curr_rgb = curr_image
            curr_gray = cv2.cvtColor(curr_rgb, cv2.COLOR_BGR2GRAY)
        else:
            curr_gray = curr_image
        
        # Ensure uint8 type
        if prev_gray.dtype != np.uint8:
            prev_gray = (prev_gray * 255).astype(np.uint8) if prev_gray.max() <= 1.0 else prev_gray.astype(np.uint8)
        if curr_gray.dtype != np.uint8:
            curr_gray = (curr_gray * 255).astype(np.uint8) if curr_gray.max() <= 1.0 else curr_gray.astype(np.uint8)
        
        # Calculate dense optical flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
        
        return flow  # (H, W, 2) - flow[y, x] = [vx, vy]
    
    def predict_future_positions(self, motion_history: List[np.ndarray], 
                                  timesteps: int = 4) -> np.ndarray:
        """
        Predict cloud positions for next timesteps (simple linear extrapolation).
        
        Args:
            motion_history: List of motion vector fields for past frames
            timesteps: Number of future timesteps to predict
        
        Returns:
            predicted_motions: (timesteps, H, W, 2) future motion vectors
        """
        if len(motion_history) == 0:
            return np.zeros((timesteps, 128, 128, 2))
        
        # Simple approach: use average of recent motion
        avg_motion = np.mean(motion_history[-3:], axis=0)
        
        # Predict future motion (linear extrapolation)
        predicted = np.stack([avg_motion * (i + 1) for i in range(timesteps)])
        
        return predicted
    
    def load_lstm_model(self, model_path: str):
        """Load LSTM model for motion prediction"""
        # Placeholder for LSTM model
        return None
    
    def calculate_cloud_velocity(self, motion_vectors: np.ndarray) -> dict:
        """
        Calculate average cloud velocity statistics
        
        Args:
            motion_vectors: (H, W, 2) motion field
            
        Returns:
            dict with velocity statistics
        """
        # Calculate magnitude
        magnitude = np.sqrt(motion_vectors[:, :, 0]**2 + motion_vectors[:, :, 1]**2)
        
        # Calculate direction (in degrees)
        direction = np.arctan2(motion_vectors[:, :, 1], motion_vectors[:, :, 0]) * 180 / np.pi
        
        return {
            'avg_speed': float(np.mean(magnitude)),
            'max_speed': float(np.max(magnitude)),
            'avg_direction': float(np.mean(direction)),
            'std_direction': float(np.std(direction))
        }


