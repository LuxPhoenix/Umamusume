"""
Mood management logic.

This module handles checking and raising character mood.
"""

from typing import Optional

from core.constants import ImagePath, MoodScore, WaitTime, GameTurn
from core.models import MoodLevel, ContinueException
from ui.image_recognition import ImageRecognition
from utils.logger import Logger

logger = Logger.get_logger()


class MoodManager:
    """Manages character mood checking and raising."""

    @staticmethod
    def get_mood_level() -> Optional[MoodLevel]:
        """
        Detect current mood level.

        Returns:
            MoodLevel enum or None if mood is Great.
        """
        bad_moods = [
            MoodLevel.AWFUL,
            MoodLevel.BAD,
            MoodLevel.NORMAL,
            MoodLevel.GOOD
        ]

        for mood in bad_moods:
            if ImageRecognition.test_image(
                f"{ImagePath.MOOD}/{mood.value}",
                confidence=0.85
            ):
                return mood

        return None  # Great mood

    @staticmethod
    def raise_mood(click_func, cfg: dict, turn: int) -> None:
        """
        Raise character's mood through recreation.

        Args:
            click_func: Function to perform clicks.
            cfg: Game configuration.
            turn: Current turn number.
        """
        if ImageRecognition.test_image(
            f"{ImagePath.GENERAL_TRAINING}/Recreation",
            confidence=0.90
        ):
            click_func(
                cfg["root"]["daily_training"]["recreation"],
                WaitTime.SHORT
            )
            logger.info(f"Turn {turn}: Raising mood via recreation")
        else:
            # Fallback for summer training
            click_func((1450, 580))
            logger.info(f"Turn {turn}: Raising mood (summer)")

        import time
        time.sleep(cfg["wait_time"]["_raise_mood_"])

    @staticmethod
    def check_mood(
        turn: int,
        raise_mood_func,
        check_date_event_func
    ) -> int:
        """
        Check mood and raise if needed.

        Args:
            turn: Current turn number.
            raise_mood_func: Function to raise mood.
            check_date_event_func: Function to check for date events.

        Returns:
            Mood score (3 for Good, 0 for Great).

        Raises:
            ContinueException: If mood was raised.
        """
        if turn == GameTurn.FIRST_TURN:
            logger.info(f"Turn {turn}: First turn, no mood check")
            return MoodScore.GREAT

        mood = MoodManager.get_mood_level()
        
        if mood is not None:
            raise_mood_func()
            check_date_event_func()
            raise ContinueException

        if ImageRecognition.test_image(f"{ImagePath.GENERAL_TRAINING}/Good"):
            logger.info(f"Turn {turn}: Mood is GOOD")
            return MoodScore.GOOD
        else:
            logger.info(f"Turn {turn}: Mood is GREAT")
            return MoodScore.GREAT
