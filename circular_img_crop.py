from PIL import Image, ImageDraw, ImageChops

img = Image.open('winnie.png').convert('RGBA')

mask = Image.new('L', img.size, 0)
draw = ImageDraw.Draw(mask)
width, height = img.size
center = (width // 2, height // 2)
radius = min(center)

draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=255)

original_alpha = img.split()[3]
new_alpha = ImageChops.multiply(original_alpha, mask)
img.putalpha(new_alpha)

img.save('winnie_circular.png')
img.show()
