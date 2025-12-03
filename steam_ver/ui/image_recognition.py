"""
Image recognition utilities.

This module handles all screen image detection and recognition operations.
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import pyautogui
from pyautogui import ImageNotFoundException

from core.constants import ImageConfidence, ImagePath
from core.models import Coordinate


class ImageRecognition:
    """Handles image recognition operations."""

    @staticmethod
    def identify_image(
        name: str,
        confidence: float = ImageConfidence.DEFAULT
    ) -> Coordinate:
        """
        Identify an image on screen and return its center coordinate.

        Args:
            name: Name of the image file (without extension).
            confidence: Confidence threshold for image matching.

        Returns:
            Coordinate of the image center.

        Raises:
            ImageNotFoundException: If image is not found on screen.
        """
        image_path = Path(ImagePath.BASE_DIR) / f"{name}.png"
        left, top, width, height = pyautogui.locateOnScreen(
            str(image_path),
            confidence=confidence
        )
        return Coordinate(left + width / 2, top + height / 2)

    @staticmethod
    def test_image(
        name: str,
        confidence: float = ImageConfidence.DEFAULT,
        region: Optional[Tuple[int, int, int, int]] = None,
        return_coordinate: bool = False
    ) -> Union[bool, Optional[Tuple[int, int, int, int]]]:
        """
        Test if an image is present on screen.

        Args:
            name: Name of the image file (without extension).
            confidence: Confidence threshold for image matching.
            region: Optional region to search (left, top, width, height).
            return_coordinate: If True, return coordinates instead of boolean.

        Returns:
            Boolean indicating presence, or coordinates if return_coordinate=True.
        """
        try:
            image_path = Path(ImagePath.BASE_DIR) / f"{name}.png"
            result = pyautogui.locateOnScreen(
                str(image_path),
                confidence=confidence,
                region=region
            )
            return result if return_coordinate else True
        except ImageNotFoundException:
            return None if return_coordinate else False

    @staticmethod
    def test_multiple_images(
        *image_names: str,
        confidence: float = ImageConfidence.DEFAULT,
        region: Optional[Tuple[int, int, int, int]] = None,
        logic: str = "or",
        directory: str = ImagePath.GENERAL_TRAINING
    ) -> bool:
        """
        Test multiple images with AND/OR logic.

        Args:
            *image_names: Names of image files to test.
            confidence: Confidence threshold for image matching.
            region: Optional region to search.
            logic: Either "or" or "and" for combining results.
            directory: Subdirectory within figures_lap.

        Returns:
            Boolean result based on specified logic.
        """
        found_count = sum(
            ImageRecognition.test_image(
                f"{directory}/{name}",
                confidence=confidence,
                region=region
            )
            for name in image_names
        )

        if found_count == 0:
            return False

        if logic == "or":
            return True
        elif logic == "and":
            return found_count == len(image_names)
        else:
            return False
