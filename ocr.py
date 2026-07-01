import os
import cv2
import easyocr

# Create EasyOCR reader only once
reader = easyocr.Reader(['en'])


def preprocess_and_read(image_path):

    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return ""

    # Read image
    image = cv2.imread(image_path)

    if image is None:
        print(f"❌ Cannot open image: {image_path}")
        return ""

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Remove noise
    gray = cv2.fastNlMeansDenoising(gray)

    # Improve contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    gray = clahe.apply(gray)

    # OCR
    results = reader.readtext(
        gray,
        detail=0,
        paragraph=True
    )

    text = " ".join(results)

    return text