import torch
import torch.nn as nn
import numpy as np

class DoubleConv(nn.Module):
    """Double convolution block for U-Net"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        return self.double_conv(x)

class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )
    
    def forward(self, x):
        return self.maxpool_conv(x)

class Up(nn.Module):
    """Upscaling then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
        self.conv = DoubleConv(in_channels, out_channels)
    
    def forward(self, x1, x2):
        x1 = self.up(x1)
        # Pad x1 to match x2 size if needed
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]
        x1 = nn.functional.pad(x1, [diffX // 2, diffX - diffX // 2,
                                     diffY // 2, diffY - diffY // 2])
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)

class CloudSegmentationModel(nn.Module):
    """
    U-Net model for cloud detection and opacity classification.
    Input: Multi-band satellite imagery (6 channels: R, G, B, NIR, SWIR, IR)
    Output: 4-class segmentation (clear, thin, thick, storm)
    """
    def __init__(self, in_channels=6, num_classes=4):
        super().__init__()
        self.in_channels = in_channels
        self.num_classes = num_classes
        
        self.inc = DoubleConv(in_channels, 64)
        self.down1 = Down(64, 128)
        self.down2 = Down(128, 256)
        self.down3 = Down(256, 512)
        self.down4 = Down(512, 1024)
        
        self.up1 = Up(1024, 512)
        self.up2 = Up(512, 256)
        self.up3 = Up(256, 128)
        self.up4 = Up(128, 64)
        
        self.outc = nn.Conv2d(64, num_classes, kernel_size=1)
    
    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        
        logits = self.outc(x)
        return logits

class CloudSegmentationInference:
    def __init__(self, model_path: str = None, device='cpu'):
        self.device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')
        self.model = CloudSegmentationModel(in_channels=6, num_classes=4)
        
        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            except FileNotFoundError:
                print(f"Warning: Model file not found at {model_path}. Using untrained model.")
            except Exception as e:
                print(f"Warning: Could not load model: {e}. Using untrained model.")
        
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, satellite_image: np.ndarray) -> np.ndarray:
        """
        Predict cloud mask from satellite imagery.
        
        Args:
            satellite_image: (H, W, 6) numpy array
        
        Returns:
            cloud_mask: (H, W) numpy array with values 0-3
                0 = clear, 1 = thin clouds, 2 = thick clouds, 3 = storm
        """
        with torch.no_grad():
            # Preprocess
            image_tensor = self.preprocess(satellite_image)
            image_tensor = image_tensor.unsqueeze(0).to(self.device)
            
            # Inference
            output = self.model(image_tensor)
            prediction = torch.argmax(output, dim=1).cpu().numpy()[0]
            
        return prediction
    
    def preprocess(self, image: np.ndarray) -> torch.Tensor:
        """Normalize and convert to tensor"""
        # Normalize to [0, 1]
        image = image.astype(np.float32)
        if image.max() > 1.0:
            image = image / 255.0
        
        # Convert to tensor and permute to (C, H, W)
        return torch.from_numpy(image).permute(2, 0, 1)

