from PIL import Image, ImageDraw, ImageFont

# Create ASCII art as image
ascii_art = """
██████████      ████████████      ██████████
████    ████            ████    ████      ████
████    ████            ████    ████
████    ████    ████████████    ████    ██████
████    ████    ████            ████      ████
████    ████    ████            ████      ████
████    ████    ████████████    ████      ████
██████████      ████████████      ██████████
"""

# Create image with red text on black background
img_size = 256
img = Image.new('RGB', (img_size, img_size), color='black')
draw = ImageDraw.Draw(img)

# Try to use a monospace font, fallback to default
try:
    font = ImageFont.truetype("consola.ttf", 18)
except:
    font = ImageFont.load_default()

# Draw the ASCII art
lines = ascii_art.strip().split('\n')
y_offset = 20
for line in lines:
    draw.text((5, y_offset), line, fill='red', font=font)
    y_offset += 25

# Save as PNG first
img.save('d:/Coding/TruTopsDWGtoGEO/d2g_ascii_icon.png')

# Create ICO with multiple sizes
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = []
for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    icons.append(resized)

icons[0].save('d:/Coding/TruTopsDWGtoGEO/d2g_icon.ico', format='ICO', sizes=[(s[0], s[1]) for s in sizes])

print("Created d2g_icon.ico successfully!")
