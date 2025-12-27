"""
Race management logic.

This module handles race-related operations like finding races,
changing strategies, and upgrading skills.
"""

import time
from typing import Dict, Any

import pyautogui
from pyautogui import ImageNotFoundException

from core.constants import ImagePath, WaitTime, SkillUpgrade, ImageConfidence
from core.models import ContinueException, WindowBounds
from ui.image_recognition import ImageRecognition
from ui.click_handler import ClickHandler
from shared.utils.logger import Logger

logger = Logger.get_logger()


class RaceManager:
    """Manages race-related operations."""

    @staticmethod
    def handle_scheduled_race(
        turn: int,
        race_days: list,
        upgrade_skills_func,
        wait_for_image_func,
        click_func,
        click_multiple_func,
        confirm_goal_func,
        cfg: Dict[str, Any],
    ) -> None:
        """
        Handle scheduled race day.

        Args:
            turn: Current turn number.
            race_days: List of scheduled race days.
            upgrade_skills_func: Function to upgrade skills.
            wait_for_image_func: Function to wait for images.
            click_func: Function to perform clicks.
            click_multiple_func: Function to perform multiple clicks.
            confirm_goal_func: Function to confirm goal.
            cfg: Game configuration.

        Raises:
            ContinueException: After race completion.
        """
        if turn not in race_days:
            return

        upgrade_skills_func()
        wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/RaceMain")

        logger.info(f"Turn {turn}: Scheduled race day")

        # Navigate to race
        wait_time = cfg["wait_time"]["_check_mainrace"]["register"]
        click_func(cfg["root"]["daily_training"]["race_day"], wait_time)
        wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/Race1")
        click_func(cfg["lobby_ui"]["race_enter"])
        wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/Race2")
        click_func(cfg["lobby_ui"]["race_confirm_button"])

        # Complete race
        wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/Result")
        click_func(cfg["lobby_ui"]["view_result_button"], 3)

        race_button_wait = cfg["wait_time"]["_check_mainrace"]["race_button"]
        click_multiple_func(cfg["lobby_ui"]["race_button"], 3, race_button_wait)

        confirm_goal_func()
        raise ContinueException

    @staticmethod
    def upgrade_skills(
        window_bounds: WindowBounds,
        wait_for_image_func,
        click_func,
        screen_reader,
        cfg: Dict[str, Any],
    ) -> None:
        """
        Upgrade character skills if possible.

        Args:
            window_bounds: Game window bounds.
            wait_for_image_func: Function to wait for images.
            click_func: Function to perform clicks.
            screen_reader: Screen text reader instance.
            cfg: Game configuration.
        """
        wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/Skills")
        click_func(cfg["race_day"]["skills"])
        time.sleep(WaitTime.MEDIUM)

        desired_skills = ["Corner Recovery O"]

        while desired_skills:
            # Search for upgradeable skill
            try:
                skill_region = (window_bounds.x + 194, window_bounds.y + 333, 469, 355)
                found = pyautogui.locateOnScreen(
                    f"{ImagePath.BASE_DIR}/{ImagePath.SKILL}/Blue.png",
                    confidence=0.8,
                    region=skill_region,
                )
            except ImageNotFoundException:
                found = None

            if found:
                # Capture skill name
                name_position = (int(found.left) + 48, int(found.top) - 20, 226, 30)
                screen_reader.capture_screen(region=name_position)
                skill_name = screen_reader.detect_text_in_image("test/screenshot.png")

                # Check if it's the desired skill
                if "Corner Recovery" in skill_name:
                    # Upgrade the skill
                    pyautogui.click(int(found.left) + 48, int(found.top) - 20)
                    pyautogui.click(1460, 546)  # Upgrade button
                    logger.info("Corner Recovery O upgraded")
                    desired_skills.remove("Corner Recovery O")

                    if not desired_skills:
                        logger.info("All desired skills upgraded")
                        break

            # Check if reached end of list
            try:
                pyautogui.locateOnScreen(
                    f"{ImagePath.BASE_DIR}/skill/skill_end.png", confidence=0.8
                )
                logger.info("Reached end of skill list")
                break
            except ImageNotFoundException:
                # Scroll down
                pyautogui.click(x=window_bounds.x + 493, y=window_bounds.y + 398)
                time.sleep(SkillUpgrade.SCROLL_WAIT)
                for _ in range(SkillUpgrade.SCROLL_COUNT):
                    pyautogui.scroll(SkillUpgrade.SCROLL_DIRECTION)
                logger.debug("Scrolled down skill list")

        click_func(cfg["race_day"]["back_button"])
        logger.info("Skill upgrade check completed")

    @staticmethod
    def find_race(
        turn: int,
        race_table: Dict[str, str],
        window_bounds: WindowBounds,
        click_func,
        cfg: Dict[str, Any],
    ) -> None:
        """
        Find and select race from list.

        Args:
            turn: Current turn number.
            race_table: Mapping of turns to race names.
            window_bounds: Game window bounds.
            click_func: Function to perform clicks.
            cfg: Game configuration.
        """
        race_name = race_table[str(turn)]
        logger.info(f"Finding race: {race_name}")

        while True:
            coord = ImageRecognition.find_image_center(
                f"{ImagePath.URA}/races/{race_name}"
            )

            if not coord:
                # Scroll to find race
                top_x, top_y = cfg["race_ui"]["top_race"]
                bottom_x, bottom_y = cfg["race_ui"]["bottom_race"]

                pyautogui.moveTo(bottom_x + window_bounds.x, bottom_y + window_bounds.y)
                pyautogui.dragTo(top_x + window_bounds.x, window_bounds.y + top_y, 1)
                time.sleep(WaitTime.MEDIUM)
            else:
                # Click on found race
                ClickHandler.click_coordinate(coord)
                break

        click_func(cfg["lobby_ui"]["race"], WaitTime.SHORT)
        click_func(cfg["lobby_ui"]["race_confirm_button"], WaitTime.SHORT)

    @staticmethod
    def change_race_strategy(turn: int, character, wait_for_image_func) -> None:
        """
        Change race strategy if needed for current turn.

        Args:
            turn: Current turn number.
            character: Character with strategy data.
            wait_for_image_func: Function to wait for images.
        """
        if turn not in character.strategy:
            return

        strategy = character.strategy[turn]

        coord = wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/ChangeStrategy")
        ClickHandler.click_coordinate(coord)

        coord = wait_for_image_func(f"{ImagePath.STRATEGY}/{strategy}")
        ClickHandler.click_coordinate(coord)

        coord = wait_for_image_func(f"{ImagePath.STRATEGY}/Confirm")
        ClickHandler.click_coordinate(coord)
