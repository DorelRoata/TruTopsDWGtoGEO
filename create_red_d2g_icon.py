from PIL import Image, ImageDraw, ImageFont
import os

ascii_art = r"""
██████████      ████████████      ██████████
████    ████            ████    ████      ████
████    ████            ████    ████
████    ████    ████████████    ████    ██████
████    ████    ████            ████      ████
████    ████    ████            ████      ████
████    ████    ████████████    ████      ████
██████████      ████████████      ██████████
"""

def create_icon():
    print("Generating D2G Red Icon...")
    
    # Configuration
    img_size = 1024 # Work with a larger canvas for better quality
    padding = 50
    target_color = (255, 0, 0, 255) # Red
    bg_color = (0, 0, 0, 0) # Transparent
    
    # Create image
    img = Image.new('RGBA', (img_size, img_size), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Determine Max Font Size that fits
    font_size = 10
    font_path = "consola.ttf" # Windows standard
    
    # Find optimal font size
    lines = ascii_art.strip().split('\n')
    max_line_len = max(len(line) for line in lines)
    
    for size in range(10, 200, 2):
        try:
            font = ImageFont.truetype(font_path, size)
        except OSError:
            # Fallback for non-windows or if font missing
            font = ImageFont.load_default()
            break
            
        # Check width
        max_w = 0
        total_h = 0
        
        # Get line height
        bbox_sample = draw.textbbox((0,0), "█", font=font)
        line_height = bbox_sample[3] - bbox_sample[1]
        # Add a little spacing
        line_height = int(line_height * 1.0) 
        
        # Calculate total dimensions
        for line in lines:
            bbox = draw.textbbox((0,0), line, font=font)
            w = bbox[2] - bbox[0]
            max_w = max(max_w, w)
            
        total_h = len(lines) * line_height
        
        if max_w > (img_size - 2*padding) or total_h > (img_size - 2*padding):
            font_size = size - 2
            break
        font_size = size
        
    print(f"Selected Font Size: {font_size}")
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()
        
    # Recalculate positions with final font
    bbox_sample = draw.textbbox((0,0), "█", font=font)
    line_height = bbox_sample[3] - bbox_sample[1] # standard height
    
    # Calculate exact bounding box of the whole block to center it
    lines_metrics = []
    block_width = 0
    block_height = 0
    
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2] - bbox[0]
        block_width = max(block_width, w)
    
    block_height = len(lines) * line_height
    
    start_x = (img_size - block_width) // 2
    start_y = (img_size - block_height) // 2
    
    # Draw
    y = start_y
    for line in lines:
        draw.text((start_x, y), line, fill=target_color, font=font)
        y += line_height

    # Save PNG
    output_png = 'd:/Coding/TruTopsDWGtoGEO/d2g_icon_red.png'
    img.save(output_png)
    print(f"Saved PNG to {output_png}")
    
    # Save ICO
    output_ico = 'd:/Coding/TruTopsDWGtoGEO/d2g_icon_red.ico'
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    img.save(output_ico, format='ICO', sizes=sizes)
    print(f"Saved ICO to {output_ico}")

if __name__ == "__main__":
    create_icon()
