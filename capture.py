from PIL import ImageGrab, Image
from typing import Tuple, Optional

class ScreenCapture:
    """Handles screen capture operations."""

    @staticmethod
    def capture_region(x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
        """
        Capture a specific region of the screen.

        Args:
            x: Left coordinate
            y: Top coordinate
            width: Width of the region
            height: Height of the region

        Returns:
            PIL Image object or None if capture fails
        """
        try:
            # ImageGrab.grab expects (left, top, right, bottom)
            bbox = (x, y, x + width, y + height)
            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    @staticmethod
    def capture_full_screen() -> Optional[Image.Image]:
        """
        Capture the entire screen.

        Returns:
            PIL Image object or None if capture fails
        """
        try:
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    @staticmethod
    def preprocess_for_ocr(image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.

        Args:
            image: PIL Image object

        Returns:
            Preprocessed PIL Image object
        """
        # Convert to grayscale
        image = image.convert('L')

        # Increase contrast
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # Increase sharpness
        sharpener = ImageEnhance.Sharpness(image)
        image = sharpener.enhance(2.0)

        # Scale up for better OCR (2x size)
        width, height = image.size
        image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)

        return image

    @staticmethod
    def save_debug_image(image: Image.Image, filename: str = "debug_capture.png"):
        """Save image for debugging purposes."""
        try:
            image.save(filename)
            print(f"Debug image saved: {filename}")
        except Exception as e:
            print(f"Error saving debug image: {e}")
