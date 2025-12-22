"""
Image recognition utilities.

This module handles all screen image detection and recognition operations.

Functions are organized by purpose:
- find_*: Locate images and return coordinates (raises exception if not found)
- check_*: Test if images exist (returns boolean, no exception)
- get_*: Get image information (returns optional values)
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

import pyautogui

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pyautogui import ImageNotFoundException

from core.constants import ImageConfidence, ImagePath
from core.models import Coordinate
from shared.utils.logger import Logger

logger = Logger.get_logger()

class ImageRecognition:
    """
    Handles image recognition operations.

    Method naming convention:
    - find_image_*: Finds image and returns coordinates (raises if not found)
    - check_image_exists: Checks if image exists (returns bool)
    - get_image_location: Gets image location (returns optional coordinates)
    """

    # ==================== FIND METHODS (Returns coordinates, raises if not found) ====================

    @staticmethod
    def find_image_center(
        name: str,
        confidence: float = ImageConfidence.DEFAULT,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Coordinate:
        """
        Find an image on screen and return its CENTER coordinate.

        **Purpose**: When you need to click on the CENTER of an image.
        **Behavior**: Raises ImageNotFoundException if image not found.

        Args:
            name: Name of the image file (without extension).
            confidence: Confidence threshold for image matching (0.0 to 1.0).
            region: Optional region to search (left, top, width, height).

        Returns:
            Coordinate of the image CENTER (x, y).
        """
        image_path = Path(ImagePath.BASE_DIR) / f"{name}.png"
        search_result = pyautogui.locateOnScreen(
            str(image_path), confidence=confidence, region=region
        )
        if search_result is None:
            raise ImageNotFoundException(f"Image '{name}' not found on screen.")

        left, top, width, height = search_result
        center_x = left + width / 2
        center_y = top + height / 2
        return Coordinate(center_x, center_y)

    @staticmethod
    def check_image_exists(
        name: str,
        confidence: float = ImageConfidence.DEFAULT,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> bool:
        """
        Check if an image exists on screen.

        **Purpose**: When you just need to know if an image is present (yes/no).
        **Behavior**: Returns True/False, never raises exception.

        Args:
            name: Name of the image file (without extension).
            confidence: Confidence threshold for image matching.
            region: Optional region to search (left, top, width, height).

        Returns:
            True if image exists, False otherwise.
        """
        image_path = Path(ImagePath.BASE_DIR) / f"{name}.png"
        try:
            result = pyautogui.locateOnScreen(
                str(image_path), confidence=confidence, region=region
            )
            # logger.info(f"Image '{image_path}' found!")
        except ImageNotFoundException:
            return False
        return result is not None
        # except (ImageNotFoundException):
        #     print(f"Image '{name}' not found on screen.")
        #     return False
