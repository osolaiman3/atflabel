import pytesseract
from PIL import Image

# Path to the image file
image_path = '../examples/white christmas.png'

# Open the image using PIL
image = Image.open(image_path)

# Use Tesseract to do OCR on the image
text = pytesseract.image_to_string(image)

# Print the extracted text
print(text)