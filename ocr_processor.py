import re
from PIL import Image
from typing import Optional

try:
    import pytesseract
except ImportError:
    pytesseract = None

class OCRProcessor:
    """Handles OCR text extraction from images."""

    def __init__(self):
        if pytesseract is None:
            raise ImportError(
                "pytesseract is not installed. "
                "Please install it with: pip install pytesseract"
            )

    @staticmethod
    def extract_number(image: Image.Image, debug: bool = False) -> Optional[float]:
        """
        Extract numerical value from image using OCR.

        Args:
            image: PIL Image object
            debug: If True, print debug information

        Returns:
            Extracted number as float, or None if extraction fails
        """
        if pytesseract is None:
            print("Error: pytesseract not available")
            return None

        try:
            # Configure Tesseract for number extraction
            # --oem 3: Use default OCR Engine Mode
            # --psm 7: Treat image as a single text line
            # -c tessedit_char_whitelist: Only recognize these characters
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.,-'

            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)

            if debug:
                print(f"OCR Raw output: '{text}'")

            # Clean and parse the number
            number = OCRProcessor._parse_number(text)

            if debug:
                print(f"Parsed number: {number}")

            return number

        except Exception as e:
            print(f"Error during OCR: {e}")
            return None

    @staticmethod
    def _parse_number(text: str) -> Optional[float]:
        """
        Parse and clean extracted text to get a number.

        Args:
            text: Raw OCR text output

        Returns:
            Cleaned number as float, or None if parsing fails
        """
        # Remove whitespace
        text = text.strip()

        if not text:
            return None

        # Common OCR corrections
        text = text.replace('O', '0')  # Letter O to zero
        text = text.replace('o', '0')
        text = text.replace('I', '1')  # Letter I to one
        text = text.replace('l', '1')  # Lowercase L to one
        text = text.replace('S', '5')  # Sometimes S is misread as 5
        text = text.replace('B', '8')  # B can be 8

        # Remove any non-numeric characters except dot, comma, and minus
        text = re.sub(r'[^0-9.,-]', '', text)

        # Handle comma as decimal separator (common in some locales)
        # If there's both comma and dot, assume comma is thousands separator
        if ',' in text and '.' in text:
            text = text.replace(',', '')
        elif ',' in text:
            text = text.replace(',', '.')

        # Remove minus signs that aren't at the start
        if '-' in text:
            is_negative = text.startswith('-')
            text = text.replace('-', '')
            if is_negative:
                text = '-' + text

        # Try to convert to float
        try:
            # Remove any duplicate dots (keep only first one)
            parts = text.split('.')
            if len(parts) > 2:
                text = parts[0] + '.' + ''.join(parts[1:])

            number = float(text)
            return number

        except ValueError:
            # If direct conversion fails, try to extract first valid number
            match = re.search(r'-?\d+\.?\d*', text)
            if match:
                try:
                    return float(match.group())
                except ValueError:
                    pass

            return None

    @staticmethod
    def test_ocr():
        """Test if Tesseract is properly installed and working."""
        if pytesseract is None:
            return False, "pytesseract module not installed"

        try:
            version = pytesseract.get_tesseract_version()
            return True, f"Tesseract version {version} is working"
        except Exception as e:
            return False, f"Tesseract not found or not working: {e}"

    @staticmethod
    def extract_multiple_numbers(image: Image.Image) -> list:
        """
        Extract all numbers found in the image.

        Args:
            image: PIL Image object

        Returns:
            List of all numbers found
        """
        if pytesseract is None:
            return []

        try:
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.,-'
            text = pytesseract.image_to_string(image, config=custom_config)

            # Find all number patterns
            numbers = []
            for match in re.finditer(r'-?\d+\.?\d*', text):
                try:
                    num = float(match.group())
                    numbers.append(num)
                except ValueError:
                    continue

            return numbers

        except Exception as e:
            print(f"Error during OCR: {e}")
            return []
