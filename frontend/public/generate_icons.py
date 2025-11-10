#!/usr/bin/env python3
"""
Generate simple icon files for SuryaDrishti
Creates favicon.ico, icon-16x16.png, icon-32x32.png, and apple-touch-icon.png
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Colors - Amber/Orange theme matching the app
BG_COLOR = (245, 158, 11)  # Amber-500 (#f59e0b)
SUN_COLOR = (255, 237, 213)  # Amber-100
DARK_COLOR = (217, 119, 6)  # Amber-600

def create_icon(size, output_path):
    """Create a simple sun icon"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw circle (sun)
    margin = size // 8
    center = size // 2
    radius = (size // 2) - margin
    
    # Outer circle (sun)
    draw.ellipse(
        [center - radius, center - radius, center + radius, center + radius],
        fill=SUN_COLOR,
        outline=BG_COLOR,
        width=max(1, size // 32)
    )
    
    # Inner circle (sun center)
    inner_radius = radius // 2
    draw.ellipse(
        [center - inner_radius, center - inner_radius, 
         center + inner_radius, center + inner_radius],
        fill=BG_COLOR
    )
    
    # Save as PNG
    img.save(output_path, 'PNG')
    print(f"Created {output_path} ({size}x{size})")

def create_favicon():
    """Create favicon.ico with proper multi-resolution ICO format"""
    try:
        from PIL import Image
        # Create 16x16, 32x32, and 48x48 images (standard ICO sizes)
        sizes = [16, 32, 48]
        images = []
        
        def draw_sun(img, size):
            draw = ImageDraw.Draw(img)
            center = size // 2
            margin = max(1, size // 8)
            radius = (size // 2) - margin
            
            # Sun circle
            draw.ellipse(
                [center - radius, center - radius, center + radius, center + radius],
                fill=SUN_COLOR,
                outline=BG_COLOR,
                width=max(1, size // 16)
            )
            # Center circle
            inner_radius = radius // 2
            draw.ellipse(
                [center - inner_radius, center - inner_radius,
                 center + inner_radius, center + inner_radius],
                fill=BG_COLOR
            )
        
        # Create images for each size
        for size in sizes:
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw_sun(img, size)
            # Convert to RGB with background for ICO
            img_rgb = Image.new('RGB', (size, size), BG_COLOR)
            if img.mode == 'RGBA':
                img_rgb.paste(img, mask=img.split()[3])
            else:
                img_rgb.paste(img)
            images.append((img_rgb, size))
        
        # Save as ICO with multiple sizes
        # PIL's ICO format supports multiple sizes
        ico_sizes = [(img.size[0], img.size[1]) for img, _ in images]
        images[0][0].save('favicon.ico', format='ICO', sizes=ico_sizes)
        print(f"Created favicon.ico with sizes: {ico_sizes}")
    except Exception as e:
        print(f"Warning: Could not create favicon.ico: {e}")
        print("Creating simple 32x32 PNG as fallback...")
        # Fallback: create a 32x32 PNG
        create_icon(32, 'favicon.png')
        print("Note: Rename favicon.png to favicon.ico if needed")

if __name__ == '__main__':
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Generating SuryaDrishti icons...")
    
    # Create PNG icons
    create_icon(16, 'icon-16x16.png')
    create_icon(32, 'icon-32x32.png')
    create_icon(180, 'apple-touch-icon.png')
    
    # Create favicon
    create_favicon()
    
    print("\n[SUCCESS] All icons generated successfully!")
    print("Files created:")
    print("  - favicon.ico")
    print("  - icon-16x16.png")
    print("  - icon-32x32.png")
    print("  - apple-touch-icon.png")

