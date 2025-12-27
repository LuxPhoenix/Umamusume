"""
Event handling logic.

This module contains handlers for various game events like inspiration, new year, choice events, etc.
"""

import time
from typing import Optional, Tuple, Dict, Any

from pyautogui import ImageNotFoundException

from core.constants import ImagePath, ChoiceOffset, WaitTime, MoodScore, ImageConfidence
from core.models import Coordinate, EventType, MoodLevel, ContinueException
from ui.image_recognition import ImageRecognition
from ui.click_handler import ClickHandler
from game_utils.event_matcher import EventMatcher
from shared.utils.logger import Logger

logger = Logger.get_logger("EventHandlers")


class EventHandlers:
    """Handlers for various game events."""

    @staticmethod
    def handle_special_event(
        coord: Coordinate,
        event_list: Dict[str, Any],
        cfg: Dict[str, Any],
        screen_reader,
        turn: int,
    ) -> None:
        """
        Handle special event that requires choice selection.

        Args:
            coord: Coordinate of the choice indicator.
            event_list: Dictionary of known events.
            cfg: Game configuration.
            screen_reader: Screen text reader instance.
            turn: Current turn number.
        """
        # Capture event text
        region = screen_reader.get_event_text_region(cfg)
        event_name = screen_reader.capture_event_text(region)

        logger.info(f"Turn {turn}: Event detected: {event_name}")

        matched_event = EventMatcher.match_event(event_name, event_list)

        if matched_event is None:
            logger.info(f"Turn {turn}: Event not in dictionary, using default")
            ClickHandler.click_coordinate(coord)
            time.sleep(WaitTime.MEDIUM)
            return

        if matched_event in event_list:
            choice = event_list[matched_event]
            if choice != "Auto":
                offset_coord = coord.offset(dy=ChoiceOffset.SECOND_CHOICE * choice)
                wait_time = cfg["wait_time"]["_check_special_"]
                ClickHandler.click_coordinate(offset_coord, wait_time)
                logger.info(
                    f"Turn {turn}: Event {matched_event}, choice {choice} selected"
                )
            else:
                logger.info(f"Turn {turn}: Auto event {matched_event}")
        else:
            wait_time = cfg["wait_time"]["_check_multiq"]
            ClickHandler.click_coordinate(coord, wait_time)
            logger.info(f"Turn {turn}: Event not found, using green option")

    @staticmethod
    def handle_inspiration_event(cfg: Dict[str, Any], turn: int) -> None:
        """
        Handle inspiration/inheriting event.

        Args:
            cfg: Game configuration.
            turn: Current turn number.
        """
        while True:
            if ImageRecognition.check_image_exists(
                f"{ImagePath.GENERAL_TRAINING}/Inheriting", confidence=0.90
            ):
                # Need to click using cfg coordinate
                logger.info(f"Turn {turn}: Inspiration event")
                time.sleep(WaitTime.VERY_LONG)
                break
            time.sleep(WaitTime.SHORT)

    @staticmethod
    def handle_new_year_event(
        wait_for_image_func, cfg: Dict[str, Any], turn: int
    ) -> None:
        """
        Handle new year event.

        Args:
            wait_for_image_func: Function to wait for images.
            cfg: Game configuration.
            turn: Current turn number.
        """
        logger.info(f"Turn {turn}: Checking for new year event")
        coord = wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/hi_g")
        logger.info(f"Turn {turn}: New year event detected")

        wait_time = cfg["wait_time"]["_check_special_"]

        if turn == 30:
            # Second choice (energy)
            offset_coord = coord.offset(dy=ChoiceOffset.SECOND_CHOICE)
            ClickHandler.click_coordinate(offset_coord, wait_time)
        else:
            # First choice (energy)
            ClickHandler.click_coordinate(coord, wait_time)

    @staticmethod
    def detect_event_type() -> Tuple[Optional[Coordinate], EventType]:
        """
        Detect current event type in the game.

        Returns:
            Tuple of (coordinate, event_type).
        """
        # Check for choice event
        try:
            coord = ImageRecognition.find_image_center(
                f"{ImagePath.GENERAL_TRAINING}/hi_g"
            )
            return coord, EventType.CHOICE_EVENT
        except ImageNotFoundException:
            pass

        # Check for training screen
        try:
            ImageRecognition.find_image_center(f"{ImagePath.GENERAL_TRAINING}/training")
            return None, EventType.TRAINING
        except ImageNotFoundException:
            pass

        # Check for race main
        try:
            ImageRecognition.find_image_center(f"{ImagePath.GENERAL_TRAINING}/RaceMain")
            return None, EventType.RACE_MAIN
        except ImageNotFoundException:
            pass

        # Default case
        return None, EventType.TRAINING

    @staticmethod
    def check_for_date_event(detect_event_func, handle_special_func, turn: int) -> None:
        """
        Check for and handle date events after mood raising.

        Args:
            detect_event_func: Function to detect event type.
            handle_special_func: Function to handle special events.
            turn: Current turn number.
        """
        time.sleep(WaitTime.VERY_LONG)

        coord, event_type = detect_event_func()

        if event_type == EventType.CHOICE_EVENT and coord is not None:
            logger.info(f"Turn {turn}: Date event detected")
            handle_special_func(coord)
        else:
            logger.info(f"Turn {turn}: No date event")

    @staticmethod
    def handle_after_race_events(
        wait_for_image_func, cfg: Dict[str, Any], turn: int
    ) -> None:
        """
        Handle events that may occur after a race.

        Args:
            wait_for_image_func: Function to wait for images.
            cfg: Game configuration.
            turn: Current turn number.

        Raises:
            ContinueException: After handling event.
        """
        while True:
            # Check for trainee event
            try:
                ImageRecognition.find_image_center(
                    f"{ImagePath.GENERAL_TRAINING}/TraineeEvent",
                    confidence=ImageConfidence.VERY_HIGH,
                )
                coord = ImageRecognition.find_image_center(
                    f"{ImagePath.GENERAL_TRAINING}/hi_g"
                )
                ClickHandler.click_coordinate(coord)
                raise ContinueException
            except ImageNotFoundException:
                pass

            # Check for support card event
            try:
                coord = ImageRecognition.find_image_center(
                    f"{ImagePath.GENERAL_TRAINING}/SupportCardEvent",
                    confidence=ImageConfidence.VERY_HIGH,
                )
                offset_coord = coord.offset(dy=ChoiceOffset.FIRST_CHOICE)
                wait_time = cfg["wait_time"]["_check_special_"]
                ClickHandler.click_coordinate(offset_coord, wait_time)
                logger.info(f"Turn {turn}: Support card event")
                raise ContinueException
            except ImageNotFoundException:
                pass

            # No more events
            time.sleep(WaitTime.SHORT)

    @staticmethod
    def check_extra_training_event(
        wait_for_image_func, capture_text_func, turn: int
    ) -> None:
        """
        Check for and handle extra training event.

        Args:
            wait_for_image_func: Function to wait for images.
            capture_text_func: Function to capture event text.
            turn: Current turn number.
        """
        time.sleep(WaitTime.VERY_LONG)
        event_name = capture_text_func()

        if event_name == "Extra Training":
            coord = wait_for_image_func(f"{ImagePath.GENERAL_TRAINING}/hi_g")
            # Click second option
            offset_coord = coord.offset(dy=81)
            ClickHandler.click_coordinate(offset_coord)
            logger.info(f"Turn {turn}: Extra training event")
        else:
            logger.debug(f"Turn {turn}: No extra training (detected: {event_name})")
