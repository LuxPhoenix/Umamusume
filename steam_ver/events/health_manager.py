"""
Health management logic.

This module handles checking infirmary and energy levels.
"""

import time

from core.constants import ImagePath, ImageConfidence, WaitTime
from core.models import ContinueException
from ui.image_recognition import ImageRecognition
from shared.utils.logger import Logger

logger = Logger.get_logger()


class HealthManager:
    """Manages character health checks."""

    @staticmethod
    def check_for_infirmary(click_func, cfg: dict, turn: int) -> bool:
        """
        Check if horse needs to go to infirmary.

        Args:
            click_func: Function to perform clicks.
            cfg: Game configuration.
            turn: Current turn number.

        Returns:
            True if went to infirmary, False otherwise.

        Raises:
            ContinueException: If infirmary visit occurred.
        """
        if ImageRecognition.check_image_exists(
            f"{ImagePath.GENERAL_TRAINING}/Infirmary",
            confidence=ImageConfidence.INFIRMARY,
        ):
            wait_time = cfg["wait_time"]["_check_mainrace"]["register"]
            click_func(cfg["root"]["daily_training"]["infirmary"], wait_time)
            time.sleep(WaitTime.LONG)
            logger.info(f"Turn {turn}: Went to infirmary")
            raise ContinueException

        logger.debug(f"Turn {turn}: Status good")
        return False

    @staticmethod
    def check_energy_level(click_func, cfg: dict, turn: int) -> bool:
        """
        Check if energy level is sufficient.

        Args:
            click_func: Function to perform clicks.
            cfg: Game configuration.
            turn: Current turn number.

        Returns:
            True if energy is sufficient, False otherwise.

        Raises:
            ContinueException: If rest was required.
        """
        energy_image_path = f"{ImagePath.GENERAL_TRAINING}/EnergyBar"
        logger.debug(f"Turn {turn}: Checking energy level using image '{energy_image_path}'")
        if ImageRecognition.check_image_exists(
            f"{ImagePath.GENERAL_TRAINING}/EnergyBar", confidence=ImageConfidence.HIGH
        ):
            logger.info(f"Turn {turn}: Energy level safe")
            return True

        logger.info(f"Turn {turn}: Energy low, resting")
        click_func(cfg["root"]["daily_training"]["rest"])
        time.sleep(cfg["wait_time"]["_check_energy_"])
        raise ContinueException
