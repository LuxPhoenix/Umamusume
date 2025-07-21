import pyautogui
import cv2
import pytesseract
from typing import Tuple, Optional

class ScreenTextReader:
    def __init__(self, tesseract_path: str = r"C://Program Files//Tesseract-OCR//tesseract.exe"):
        """
        Init OCR Screen Reader with Tesseract OCR path
        
        Args:
            tesseract_path: path to tesseract.exe
        """
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.screenshot_path = "test/screenshot.png"
        self.cropped_image_path = "test/cropped_image.png"
    
    def capture_screen(self, region: Tuple[int, int, int, int]) -> str:
        """
        Capture a screenshot of the specified region
        """
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(self.screenshot_path)
        return self.screenshot_path
    
    def detect_text_in_image(self, image_path: Optional[str] = None, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Detect text in an image using Tesseract OCR
        """
        # Use the provided image path or the default screenshot path
        img_path = image_path if image_path else self.screenshot_path
        image = cv2.imread(img_path)
        
        if region:
            x1, y1, x2, y2 = region
            x_start, x_end = min(x1, x2), max(x1, x2)
            y_start, y_end = min(y1, y2), max(y1, y2)
            cropped_img = image[y_start:y_end, x_start:x_end]
            cv2.imwrite(self.cropped_image_path, cropped_img)
        else:
            cropped_img = image
        
        text = pytesseract.image_to_string(cropped_img, lang='eng')
        return text.strip()