"""
Click handling utilities.

This module handles all mouse click operations.
"""

import time

import pyautogui

from core.constants import WaitTime
from core.models import Coordinate
from ui.image_recognition import ImageRecognition


class ClickHandler:
    """Handles click operations."""

    @staticmethod
    def click_absolute(x: float, y: float, interval: float = WaitTime.SHORT) -> None:
        """
        Click at absolute screen coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.
            interval: Wait time after click in seconds.
        """
        pyautogui.click(x, y)
        time.sleep(interval)

    @staticmethod
    def click_coordinate(coord: Coordinate, interval: float = WaitTime.SHORT) -> None:
        """
        Click at a Coordinate object.

        Args:
            coord: Coordinate to click.
            interval: Wait time after click in seconds.
        """
        ClickHandler.click_absolute(coord.x, coord.y, interval)

    @staticmethod
    def click_image(name: str) -> None:
        """
        Click on an image by name.

        Args:
            name: Name of the image to click.

        Raises:
            ImageNotFoundException: If image is not found.
        """
        coord = ImageRecognition.find_image_center(name)
        ClickHandler.click_coordinate(coord, WaitTime.MEDIUM)
