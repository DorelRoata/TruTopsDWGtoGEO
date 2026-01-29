from PIL import Image, ImageDraw, ImageFont

# Create a simple D2G icon - red text on black background
img_size = 256
img = Image.new('RGBA', (img_size, img_size), color=(0, 0, 0, 255))
draw = ImageDraw.Draw(img)

# Try to use Arial Bold, fallback to default
try:
    font = ImageFont.truetype("arialbd.ttf", 80)
except:
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()

# Draw "D2G" centered
text = "D2G"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (img_size - text_width) // 2
y = (img_size - text_height) // 2 - 10

draw.text((x, y), text, fill=(255, 0, 0, 255), font=font)

# Save as PNG first to verify
img.save('d:/Coding/TruTopsDWGtoGEO/d2g_simple.png', 'PNG')
print("Created d2g_simple.png")

# Create proper ICO file with multiple sizes
ico_sizes = [256, 128, 64, 48, 32, 16]
img.save('d:/Coding/TruTopsDWGtoGEO/d2g_simple.ico', format='ICO', sizes=[(s, s) for s in ico_sizes])
print("Created d2g_simple.ico successfully!")
