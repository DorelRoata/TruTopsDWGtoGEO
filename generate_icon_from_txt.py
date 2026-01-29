from PIL import Image, ImageDraw, ImageFont

# Read ASCII art from file
try:
    with open('d2g_logo.txt', 'r', encoding='utf-8') as f:
        ascii_art = f.read()
except Exception as e:
    print(f"Error reading logo file: {e}")
    exit(1)

print("Using ASCII Art:")
print(ascii_art)

# Create image with red text on transparent background
# Calculated size: 8 lines vertical, ~45 chars horizontal.
img_size = 512
img = Image.new('RGBA', (img_size, img_size), color=(0, 0, 0, 0)) # Transparent
draw = ImageDraw.Draw(img)

# Try to use a monospace font
try:
    # Consolas is standard on Windows
    font = ImageFont.truetype("consola.ttf", 30)
except:
    try:
        font = ImageFont.truetype("cour.ttf", 30) # Courier New
    except:
        font = ImageFont.load_default()

# Draw the ASCII art centered
lines = ascii_art.strip().split('\n')
line_height = 30 # Approx for size 40 font? need to measure
# Better way to measure:
bbox = draw.textbbox((0, 0), lines[0], font=font)
char_height = bbox[3] - bbox[1] + 5 # include some line spacing

total_height = len(lines) * char_height
max_width = 0
for line in lines:
    bbox = draw.textbbox((0, 0), line, font=font)
    w = bbox[2] - bbox[0]
    if w > max_width:
        max_width = w

start_x = (img_size - max_width) // 2
start_y = (img_size - total_height) // 2

y_offset = start_y
for line in lines:
    draw.text((start_x, y_offset), line, fill=(255, 0, 0, 255), font=font)
    y_offset += char_height

# Save as PNG first
img.save('d:/Coding/TruTopsDWGtoGEO/d2g_custom_icon.png')

# Create ICO
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = []
for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    icons.append(resized)

icons[0].save('d:/Coding/TruTopsDWGtoGEO/d2g_custom.ico', format='ICO', sizes=[(s[0], s[1]) for s in sizes])

print("Created d2g_custom.ico successfully!")
