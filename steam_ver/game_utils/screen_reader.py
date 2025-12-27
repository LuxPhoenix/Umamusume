"""
Screen reading utilities wrapper.

This module wraps the screen text reader with game-specific functionality.
"""

from typing import Tuple, Dict, Any

from utils.detect_text import ScreenTextReader


class GameScreenReader:
    """Wrapper for screen text reading with game-specific methods."""

    def __init__(self, window_bounds):
        """Initialize with window bounds."""
        self.screen_reader = ScreenTextReader()
        self.window_bounds = window_bounds

    def get_event_text_region(self, cfg: Dict[str, Any]) -> Tuple[int, int, int, int]:
        """
        Get the screen region for event text.

        Args:
            cfg: Game configuration.

        Returns:
            Tuple of (top, left, bottom, right).
        """
        event_region = cfg["event_capture"]["event_text"]
        top, left = event_region["top_left"]
        bottom, right = event_region["bottom_right"]
        return (top, left, bottom, right)

    def capture_event_text(self, text_region: Tuple[int, int, int, int]) -> str:
        """
        Capture and detect event text from screen.

        Args:
            text_region: Region to capture text from.

        Returns:
            Detected event text.
        """
        region = (
            self.window_bounds.x,
            self.window_bounds.y,
            self.window_bounds.width,
            self.window_bounds.height
        )
        self.screen_reader.capture_screen(region=region)
        return self.screen_reader.detect_text_in_image(
            "test/screenshot.png",
            text_region
        )

    def capture_screen(self, region=None):
        """Capture screen region."""
        return self.screen_reader.capture_screen(region=region)

    def detect_text_in_image(self, image_path: str, region=None):
        """Detect text in image."""
        return self.screen_reader.detect_text_in_image(image_path, region)
