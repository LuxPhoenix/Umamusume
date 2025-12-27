import pyautogui
import cv2
import pytesseract
import numpy as np
from typing import Tuple, Optional
from concurrent.futures import ThreadPoolExecutor

from services import ConfigService
from config.paths import Paths


class ScreenTextReader:
    def __init__(
        self, tesseract_path: str = r"C://Program Files//Tesseract-OCR//tesseract.exe"
    ):
        """
        Init OCR Screen Reader with Tesseract OCR path.

        Args:
            tesseract_path: path to tesseract.exe
        """
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Use Paths for file locations
        Paths.ensure_dir_exists(Paths.TEST_DIR)
        self.screenshot_path = str(Paths.TEST_DIR / "screenshot.png")
        self.cropped_image_path = str(Paths.TEST_DIR / "cropped_image.png")

        self.config = self.setup_config()

    def setup_config(self) -> dict:
        """Load configuration from dictionary file."""
        return ConfigService.load_dictionary()

    def capture_screen(self, region: Tuple[int, int, int, int]) -> str:
        """
        Capture a screenshot of the specified region
        """
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(self.screenshot_path)
        return self.screenshot_path

    def detect_text_in_image(
        self,
        image_path: Optional[str] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        config=None,
    ) -> str:
        """
        Detect text in an image using Tesseract OCR
        Get the whole image if no region is specified else crop to the region
        Then read text from the cropped image
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

        if config:
            text = pytesseract.image_to_string(cropped_img, config=config)
        else:
            text = pytesseract.image_to_string(cropped_img, lang="eng")
        return text.strip()

    def clean_number(self, text: str) -> str:
        return "".join(filter(str.isdigit, text))

    def detect_one_stat(self, x, y, w, h) -> str:
        box = (x, y, w, h)
        # Chụp ảnh trực tiếp thay vì lưu file để tránh xung đột
        screenshot = pyautogui.screenshot(region=box)
        # Chuyển đổi PIL image thành numpy array cho OpenCV
        import numpy as np

        image_array = np.array(screenshot)
        # Chuyển đổi RGB thành BGR cho OpenCV
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

        stat = pytesseract.image_to_string(image_array, config="--psm 12")
        stat = self.clean_number(stat)
        if stat and stat.isdigit():  # Chỉ trả về nếu là số hợp lệ
            return stat
        else:
            return ""

    def detect_stat(self, x, y) -> dict:
        position_stat_cfg = self.config["stat_position"]

        executor = ThreadPoolExecutor(max_workers=5)
        task = []
        for stat_name, pos in position_stat_cfg.items():
            final_x = x + pos[0]
            final_y = y + pos[1]
            print(f"Debug - {stat_name}: position ({final_x}, {final_y})")
            task.append(executor.submit(self.detect_one_stat, final_x, final_y, 40, 20))

        results = [t.result() for t in task]

        stats = {stat: text for stat, text in zip(position_stat_cfg.keys(), results)}
        print(f"Debug - Final stats: {stats}")
        return stats
