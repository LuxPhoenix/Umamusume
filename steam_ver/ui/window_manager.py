"""
Window management utilities.

This module handles game window operations like positioning and resizing.
"""

import pygetwindow as gw

from core.constants import GameWindow
from core.models import WindowBounds, UmaException


class WindowManager:
    """Manages game window operations."""

    @staticmethod
    def get_game_window() -> gw.Win32Window:
        """
        Get the game window object.

        Returns:
            Game window object.

        Raises:
            UmaException: If game window is not found.
        """
        windows = gw.getWindowsWithTitle(GameWindow.TITLE)
        if not windows:
            raise UmaException(f"Window '{GameWindow.TITLE}' not found")
        return windows[0]

    @staticmethod
    def resize_window(window: gw.Win32Window, target_width: int) -> None:
        """
        Resize window maintaining aspect ratio.

        Args:
            window: Window to resize.
            target_width: Target width in pixels.
        """
        aspect_ratio = window.width / window.height
        new_height = int(target_width / aspect_ratio)
        window.resizeTo(target_width, new_height)

    @staticmethod
    def get_window_bounds(window: gw.Win32Window) -> WindowBounds:
        """
        Get window position and dimensions.

        Args:
            window: Window to get bounds from.

        Returns:
            WindowBounds object.
        """
        return WindowBounds(
            x=window.left,
            y=window.top,
            width=window.width,
            height=window.height
        )

    @staticmethod
    def setup_game_window() -> WindowBounds:
        """
        Setup game window with standard dimensions.

        Returns:
            WindowBounds of the configured window.
        """
        window = WindowManager.get_game_window()
        WindowManager.resize_window(window, GameWindow.TARGET_WIDTH)
        return WindowManager.get_window_bounds(window)
