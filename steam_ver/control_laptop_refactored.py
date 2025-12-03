"""
Umamusume Game Automation Controller.

This module provides automated control for the Umamusume game on Steam,
handling training loops, racing events, and UI interactions.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Union

import jiwer
import pyautogui
import pygetwindow as gw
from pyautogui import ImageNotFoundException

from horse_info import HorseGirl, El_Condor, SupportCard
from utils.detect_text import ScreenTextReader
from utils.logger import Logger

# Module-level logger
logger = Logger.get_logger()


# Constants
class GameWindow:
    """Game window configuration constants."""
    TITLE = "Umamusume"
    TARGET_WIDTH = 1440


class TrainingType(Enum):
    """Enumeration of training types."""
    SPEED = "speed"
    STAMINA = "stamina"
    POWER = "power"
    GUTS = "guts"
    WITS = "wits"


class EventType(Enum):
    """Enumeration of event types."""
    CHOICE_EVENT = "choice_event"
    TRAINING = "training"
    RACE_MAIN = "race_main"


class GameTurn:
    """Turn-related constants."""
    MAX_TURN = 80
    URA_START_TURN = 72
    INSPIRATION_TURNS = [30, 54]
    NEW_YEAR_TURNS = [24, 48]
    FIRST_TURN = 0


class ImageConfidence:
    """Default confidence levels for image recognition."""
    DEFAULT = 0.9
    HIGH = 0.97
    VERY_HIGH = 0.99
    INFIRMARY = 0.997


class WaitTime:
    """Default wait times in seconds."""
    SHORT = 0.5
    MEDIUM = 2.0
    LONG = 4.0
    VERY_LONG = 10.0


class ImagePath:
    """Image path constants."""
    BASE_DIR = "figures_lap"
    GENERAL_TRAINING = "generaltraining"
    MOOD = "mood"
    URA = "URA"
    STRATEGY = "strategy"
    SKILL = "skill"


class ChoiceOffset:
    """Offset for choice button positions."""
    FIRST_CHOICE = 0
    SECOND_CHOICE = 82
    THIRD_CHOICE = 164


class MoodLevel(Enum):
    """Mood level enumeration."""
    AWFUL = "Awful"
    BAD = "Bad"
    NORMAL = "Normal"
    GOOD = "Good"
    GREAT = "Great"


class MoodScore:
    """Mood score constants."""
    GOOD = 3
    GREAT = 0


class FriendshipColor:
    """RGB color constants for friendship detection."""
    ORANGE_R = 243
    ORANGE_G = 177
    ORANGE_B = 69
    COLOR_THRESHOLD = 72


class TrainingScore:
    """Training score multipliers."""
    DIRECTOR_BONUS = 0.3
    REPORTER_BONUS = 0.3


class SkillUpgrade:
    """Skill upgrade constants."""
    SCROLL_COUNT = 8
    SCROLL_DIRECTION = -1
    SCROLL_WAIT = 5


class EventMatching:
    """Event matching thresholds."""
    WER_THRESHOLD = 0.25


@dataclass
class WindowBounds:
    """Represents window position and dimensions."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class Coordinate:
    """Represents a 2D coordinate."""
    x: float
    y: float

    def offset(self, dx: float = 0, dy: float = 0) -> Coordinate:
        """Return a new coordinate with offset applied."""
        return Coordinate(self.x + dx, self.y + dy)

    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple."""
        return (self.x, self.y)


class UmaException(Exception):
    """Base exception for Uma game errors."""
    pass


class ContinueException(Exception):
    """Exception to signal continuation to next turn."""
    pass


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


class ClickHandler:
    """Handles click operations."""

    @staticmethod
    def click_absolute(
        x: float,
        y: float,
        interval: float = WaitTime.SHORT
    ) -> None:
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
    def click_coordinate(
        coord: Coordinate,
        interval: float = WaitTime.SHORT
    ) -> None:
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
        coord = ImageRecognition.identify_image(name)
        ClickHandler.click_coordinate(coord, WaitTime.MEDIUM)


class ConfigLoader:
    """Handles configuration file loading."""

    @staticmethod
    def load_dictionary() -> Dict[str, Any]:
        """Load the main dictionary configuration."""
        config_path = Path("data/json/dictionary.json")
        with open(config_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def load_deck_config(deck_name: str) -> Optional[Dict[str, Any]]:
        """
        Load deck-specific configuration.

        Args:
            deck_name: Name of the deck.

        Returns:
            Deck configuration or None if not found.
        """
        config_path = Path(f"data/json/{deck_name}.json")
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            logger.warning(f"Deck config not found: {deck_name}")
            return None

    @staticmethod
    def load_support_card_data(card_name: str) -> Dict[str, Any]:
        """
        Load support card data.

        Args:
            card_name: Name of the support card.

        Returns:
            Support card data dictionary.
        """
        card_path = Path(f"data/support_card_data/{card_name}.json")
        with open(card_path, "r", encoding="utf-8") as file:
            return json.load(file)


class WindowManager:
    """Manages game window operations."""

    @staticmethod
    def get_game_window() -> gw.Win32Window:
        """
        Get the game window object.

        Returns:
            Game window object.

        Raises:
            IndexError: If game window is not found.
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


class EventMatcher:
    """Handles event matching using text similarity."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison.

        Args:
            text: Text to normalize.

        Returns:
            Normalized text.
        """
        return jiwer.RemovePunctuation()(text.lower())

    @staticmethod
    def match_event(
        detected_name: str,
        event_list: Dict[str, Any]
    ) -> Optional[str]:
        """
        Match detected event name to known events using WER.

        Args:
            detected_name: Detected event name.
            event_list: Dictionary of known events.

        Returns:
            Matched event name or None if no good match found.
        """
        if not event_list:
            return None

        best_match = None
        best_score = float('inf')
        
        norm_detected = EventMatcher.normalize_text(detected_name)

        for key in event_list.keys():
            norm_key = EventMatcher.normalize_text(key)
            score = jiwer.wer(norm_detected, norm_key)
            
            if score < best_score:
                best_score = score
                best_match = key

        if best_score < EventMatching.WER_THRESHOLD:
            return best_match
        return None


class UmaGame:
    """Main game automation controller."""

    def __init__(
        self,
        support_card: Optional[Tuple[SupportCard, ...]] = None,
        race_day: Optional[List[int]] = None,
        manual_race_day: Optional[List[int]] = None,
        test: bool = True,
        deck_name: str = "Cap",
        character: HorseGirl = El_Condor
    ) -> None:
        """
        Initialize the game controller.

        Args:
            support_card: Tuple of support cards (unused in current implementation).
            race_day: List of scheduled race days (unused).
            manual_race_day: List of manual race days (unused).
            test: Test mode flag.
            deck_name: Name of the deck configuration to use.
            character: HorseGirl character to train.
        """
        self.test = test
        self.character = character
        self.deck_name = deck_name

        # Game state
        self.turn = GameTurn.FIRST_TURN
        self.style: Optional[str] = None
        self.strategy: Optional[str] = None
        self.pre_trainoption: int = 0

        # Configuration
        self.cfg = ConfigLoader.load_dictionary()
        self.event_manage = ConfigLoader.load_deck_config(deck_name)
        self.list_event = self._setup_event_dictionary(self.event_manage)

        # Window setup
        self.window_bounds = WindowManager.setup_game_window()

        # Screen reader
        self.screen_reader = ScreenTextReader()

    def _setup_event_dictionary(
        self,
        event_manage: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Setup flattened event dictionary.

        Args:
            event_manage: Event management configuration.

        Returns:
            Flattened event dictionary.
        """
        if event_manage is None:
            return {}

        special_events = {}
        for key, value in event_manage.items():
            if key not in ("manual_race_day", "race_day"):
                if isinstance(value, dict):
                    special_events.update(value)

        return special_events

    def _relative_to_absolute(self, coord: Tuple[float, float]) -> Coordinate:
        """
        Convert game-relative coordinates to absolute screen coordinates.

        Args:
            coord: Tuple of (x, y) coordinates relative to game window.

        Returns:
            Absolute screen coordinate.
        """
        x, y = coord
        return Coordinate(
            self.window_bounds.x + x,
            self.window_bounds.y + y
        )

    def click(
        self,
        coord: Union[Tuple[float, float], List[float]],
        interval: float = WaitTime.SHORT
    ) -> None:
        """
        Click at game-relative coordinates.

        Args:
            coord: Coordinates relative to game window.
            interval: Wait time after click.
        """
        abs_coord = self._relative_to_absolute(tuple(coord))
        ClickHandler.click_coordinate(abs_coord, interval)

    def click_multiple(
        self,
        coord: Union[Tuple[float, float], List[float]],
        count: int,
        interval: float = WaitTime.SHORT
    ) -> None:
        """
        Click multiple times at same location.

        Args:
            coord: Coordinates relative to game window.
            count: Number of clicks.
            interval: Wait time between clicks.
        """
        if count <= 1:
            self.click(coord, interval)
            return

        abs_coord = self._relative_to_absolute(tuple(coord))
        for _ in range(count):
            ClickHandler.click_coordinate(abs_coord, interval)

    def wait_for_image(
        self,
        image_path: str,
        confidence: float = ImageConfidence.DEFAULT,
        check_interval: float = WaitTime.SHORT
    ) -> Coordinate:
        """
        Wait for an image to appear on screen.

        Args:
            image_path: Path to image file.
            confidence: Confidence threshold.
            check_interval: Time between checks.

        Returns:
            Coordinate where image was found.
        """
        while True:
            try:
                coord = ImageRecognition.identify_image(
                    image_path,
                    confidence=confidence
                )
                return coord
            except ImageNotFoundException:
                time.sleep(check_interval)

    def detect_event_type(self) -> Tuple[Optional[Coordinate], EventType]:
        """
        Detect current event type in the game.

        Returns:
            Tuple of (coordinate, event_type).
        """
        # Check for choice event
        try:
            coord = ImageRecognition.identify_image(
                f"{ImagePath.GENERAL_TRAINING}/hi_g"
            )
            return coord, EventType.CHOICE_EVENT
        except ImageNotFoundException:
            pass

        # Check for training screen
        try:
            ImageRecognition.identify_image(
                f"{ImagePath.GENERAL_TRAINING}/training"
            )
            return None, EventType.TRAINING
        except ImageNotFoundException:
            pass

        # Check for race main
        try:
            ImageRecognition.identify_image(
                f"{ImagePath.GENERAL_TRAINING}/RaceMain"
            )
            return None, EventType.RACE_MAIN
        except ImageNotFoundException:
            pass

        # Default case - keep checking
        return None, EventType.TRAINING

    def get_event_text_region(self) -> Tuple[int, int, int, int]:
        """
        Get the screen region for event text.

        Returns:
            Tuple of (top, left, bottom, right).
        """
        event_region = self.cfg["event_capture"]["event_text"]
        top, left = event_region["top_left"]
        bottom, right = event_region["bottom_right"]
        return (top, left, bottom, right)

    def capture_event_text(self) -> str:
        """
        Capture and detect event text from screen.

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

        text_region = self.get_event_text_region()
        return self.screen_reader.detect_text_in_image(
            "test/screenshot.png",
            text_region
        )

    def handle_special_event(self, coord: Coordinate) -> None:
        """
        Handle special event that requires choice selection.

        Args:
            coord: Coordinate of the choice indicator.
        """
        event_name = self.capture_event_text()
        logger.info(f"Turn {self.turn}: Event detected: {event_name}")

        matched_event = EventMatcher.match_event(event_name, self.list_event)

        if matched_event is None:
            logger.info(
                f"Turn {self.turn}: Event not in dictionary, using default"
            )
            ClickHandler.click_coordinate(coord)
            return

        if matched_event in self.list_event:
            choice = self.list_event[matched_event]
            if choice != "Auto":
                offset_coord = coord.offset(
                    dy=ChoiceOffset.SECOND_CHOICE * choice
                )
                wait_time = self.cfg["wait_time"]["_check_special_"]
                ClickHandler.click_coordinate(offset_coord, wait_time)
                logger.info(
                    f"Turn {self.turn}: Event {matched_event}, "
                    f"choice {choice} selected"
                )
            else:
                logger.info(
                    f"Turn {self.turn}: Auto event {matched_event}"
                )
        else:
            wait_time = self.cfg["wait_time"]["_check_multiq"]
            ClickHandler.click_coordinate(coord, wait_time)
            logger.info(
                f"Turn {self.turn}: Event not found, using green option"
            )

    def check_for_infirmary(self) -> bool:
        """
        Check if horse needs to go to infirmary.

        Returns:
            True if went to infirmary, False otherwise.

        Raises:
            ContinueException: If infirmary visit occurred.
        """
        if ImageRecognition.test_image(
            f"{ImagePath.GENERAL_TRAINING}/Infirmary",
            confidence=ImageConfidence.INFIRMARY
        ):
            wait_time = self.cfg["wait_time"]["_check_mainrace"]["register"]
            self.click(
                self.cfg["root"]["daily_training"]["infirmary"],
                wait_time
            )
            time.sleep(WaitTime.LONG)
            logger.info(f"Turn {self.turn}: Went to infirmary")
            raise ContinueException

        logger.debug(f"Turn {self.turn}: Status good")
        return False

    def check_energy_level(self) -> bool:
        """
        Check if energy level is sufficient.

        Returns:
            True if energy is sufficient, False otherwise.

        Raises:
            ContinueException: If rest was required.
        """
        if ImageRecognition.test_image(
            f"{ImagePath.GENERAL_TRAINING}/EnergyBar",
            confidence=ImageConfidence.HIGH
        ):
            logger.info(f"Turn {self.turn}: Energy level safe")
            return True

        logger.info(f"Turn {self.turn}: Energy low, resting")
        self.click(self.cfg['root']['daily_training']['rest'])
        time.sleep(self.cfg["wait_time"]["_check_energy_"])
        raise ContinueException

    def get_mood_level(self) -> Optional[MoodLevel]:
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

    def raise_mood(self) -> None:
        """Raise character's mood through recreation."""
        if ImageRecognition.test_image(
            f"{ImagePath.GENERAL_TRAINING}/Recreation",
            confidence=0.90
        ):
            self.click(
                self.cfg["root"]["daily_training"]["recreation"],
                WaitTime.SHORT
            )
            logger.info(f"Turn {self.turn}: Raising mood via recreation")
        else:
            # Fallback for summer training
            self.click((1450, 580))
            logger.info(f"Turn {self.turn}: Raising mood (summer)")

        time.sleep(self.cfg["wait_time"]["_raise_mood_"])

    def check_for_date_event(self) -> None:
        """Check for and handle date events after mood raising."""
        time.sleep(WaitTime.VERY_LONG)

        self.capture_event_text()
        coord, event_type = self.detect_event_type()

        if event_type == EventType.CHOICE_EVENT and coord is not None:
            logger.info(f"Turn {self.turn}: Date event detected")
            self.handle_special_event(coord)
        else:
            logger.info(f"Turn {self.turn}: No date event")

    def check_mood(self) -> int:
        """
        Check mood and raise if needed.

        Returns:
            Mood score (3 for Good, 0 for Great).

        Raises:
            ContinueException: If mood was raised.
        """
        if self.turn == GameTurn.FIRST_TURN:
            logger.info(f"Turn {self.turn}: First turn, no mood check")
            return MoodScore.GREAT

        mood = self.get_mood_level()
        
        if mood is not None:
            self.raise_mood()
            self.check_for_date_event()
            raise ContinueException

        if ImageRecognition.test_image(
            f"{ImagePath.GENERAL_TRAINING}/Good"
        ):
            logger.info(f"Turn {self.turn}: Mood is GOOD")
            return MoodScore.GOOD
        else:
            logger.info(f"Turn {self.turn}: Mood is GREAT")
            return MoodScore.GREAT

    def handle_inspiration_event(self) -> None:
        """Handle inspiration/inheriting event."""
        while True:
            if ImageRecognition.test_image(
                f"{ImagePath.GENERAL_TRAINING}/Inheriting",
                confidence=0.90
            ):
                self.click(self.cfg["trouble_shoot"]["inheriting"])
                logger.info(f"Turn {self.turn}: Inspiration event")
                time.sleep(WaitTime.VERY_LONG)
                break
            time.sleep(WaitTime.SHORT)

    def handle_new_year_event(self) -> None:
        """Handle new year event."""
        logger.info(f"Turn {self.turn}: Checking for new year event")
        coord = self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/hi_g")
        logger.info(f"Turn {self.turn}: New year event detected")

        wait_time = self.cfg["wait_time"]["_check_special_"]
        
        if self.turn == 30:
            # Second choice (energy)
            offset_coord = coord.offset(dy=ChoiceOffset.SECOND_CHOICE)
            ClickHandler.click_coordinate(offset_coord, wait_time)
        else:
            # First choice (energy)
            ClickHandler.click_coordinate(coord, wait_time)

    def handle_choice_events(self) -> None:
        """Handle all choice events before training."""
        coord, event_type = self.detect_event_type()

        if event_type == EventType.TRAINING:
            logger.info(f"Turn {self.turn}: No choice event, training UI")
        elif event_type == EventType.CHOICE_EVENT and coord is not None:
            logger.info(f"Turn {self.turn}: Choice event detected")
            self.handle_special_event(coord)
        else:
            logger.info(f"Turn {self.turn}: Race main screen")

    def handle_scheduled_race(self) -> None:
        """
        Handle scheduled race day.

        Raises:
            ContinueException: After race completion.
        """
        if self.turn not in self.event_manage.get("race_day", []):
            return

        self.upgrade_skills()
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/RaceMain")

        logger.info(f"Turn {self.turn}: Scheduled race day")

        # Navigate to race
        wait_time = self.cfg["wait_time"]["_check_mainrace"]["register"]
        self.click(
            self.cfg["root"]["daily_training"]["race_day"],
            wait_time
        )
        self.wait_for_image(f'{ImagePath.GENERAL_TRAINING}/Race1')
        self.click(self.cfg["lobby_ui"]["race_enter"])
        self.wait_for_image(f'{ImagePath.GENERAL_TRAINING}/Race2')
        self.click(self.cfg["lobby_ui"]["race_confirm_button"])

        # Complete race
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Result")
        self.click(self.cfg["lobby_ui"]["view_result_button"], 3)
        
        race_button_wait = self.cfg["wait_time"]["_check_mainrace"]["race_button"]
        self.click_multiple(
            self.cfg["lobby_ui"]["race_button"],
            3,
            race_button_wait
        )
        
        self.confirm_goal_completion()
        raise ContinueException

    def upgrade_skills(self) -> None:
        """Upgrade character skills if possible."""
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Skills")
        self.click(self.cfg["race_day"]["skills"])
        time.sleep(WaitTime.MEDIUM)

        desired_skills = ['Corner Recovery O']
        
        while desired_skills:
            # Search for upgradeable skill
            try:
                skill_region = (
                    self.window_bounds.x + 194,
                    self.window_bounds.y + 333,
                    469,
                    355
                )
                found = pyautogui.locateOnScreen(
                    f"{ImagePath.BASE_DIR}/{ImagePath.SKILL}/Blue.png",
                    confidence=0.8,
                    region=skill_region
                )
            except ImageNotFoundException:
                found = None

            if found:
                # Capture skill name
                name_position = (
                    int(found.left) + 48,
                    int(found.top) - 20,
                    226,
                    30
                )
                self.screen_reader.capture_screen(region=name_position)
                skill_name = self.screen_reader.detect_text_in_image(
                    'test/screenshot.png'
                )

                # Check if it's the desired skill
                if 'Corner Recovery' in skill_name:
                    # Upgrade the skill
                    pyautogui.click(
                        int(found.left) + 48,
                        int(found.top) - 20
                    )
                    pyautogui.click(1460, 546)  # Upgrade button
                    logger.info("Corner Recovery O upgraded")
                    desired_skills.remove('Corner Recovery O')
                    
                    if not desired_skills:
                        logger.info("All desired skills upgraded")
                        break

            # Check if reached end of list
            try:
                pyautogui.locateOnScreen(
                    f"{ImagePath.BASE_DIR}/skill_end.png",
                    confidence=0.8
                )
                logger.info("Reached end of skill list")
                break
            except ImageNotFoundException:
                # Scroll down
                pyautogui.click(
                    x=self.window_bounds.x + 493,
                    y=self.window_bounds.y + 398
                )
                time.sleep(SkillUpgrade.SCROLL_WAIT)
                for _ in range(SkillUpgrade.SCROLL_COUNT):
                    pyautogui.scroll(SkillUpgrade.SCROLL_DIRECTION)
                logger.debug("Scrolled down skill list")

        self.click(self.cfg["race_day"]["back_button"])
        logger.info("Skill upgrade check completed")

    def confirm_goal_completion(self) -> None:
        """Confirm goal completion after race."""
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Next")
        self.click(self.cfg["lobby_ui"]["next_button"])
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Next")
        self.click(self.cfg["lobby_ui"]["next_button"])

    def handle_manual_race(self) -> None:
        """Handle manually scheduled race."""
        logger.info(f"Turn {self.turn}: Manual race scheduled")
        
        wait_time = self.cfg["wait_time"]["_check_mainrace"]["register"]
        self.click(
            self.cfg["root"]["daily_training"]["race_day"],
            wait_time
        )
        
        self.find_race()
        
        wait_time = self.cfg["wait_time"]["_check_mainrace"]["register"]
        self.click(self.cfg["lobby_ui"]["race_enter"], wait_time)
        
        event_wait = self.cfg["wait_time"]["_check_mainrace"]["event_wait"]
        self.click(self.cfg["lobby_ui"]["race_confirm_button"], event_wait)
        
        self.change_race_strategy()
        
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Result")
        
        result_wait = self.cfg["wait_time"]["_check_mainrace"]["result_button"]
        self.click_multiple(
            self.cfg["lobby_ui"]["view_result_button"],
            3,
            result_wait
        )
        
        coord = self.wait_for_image(
            f"{ImagePath.GENERAL_TRAINING}/NextRace"
        )
        ClickHandler.click_coordinate(coord)

    def find_race(self) -> None:
        """Find and select race from list."""
        race_name = self.event_manage["race_table"][str(self.turn)]
        logger.info(f"Finding race: {race_name}")

        while True:
            coord = ImageRecognition.test_image(
                f"{ImagePath.URA}/races/{race_name}",
                return_coordinate=True
            )
            
            if not coord:
                # Scroll to find race
                top_x, top_y = self.cfg["race_ui"]["top_race"]
                bottom_x, bottom_y = self.cfg["race_ui"]["bottom_race"]
                
                pyautogui.moveTo(
                    bottom_x + self.window_bounds.x,
                    bottom_y + self.window_bounds.y
                )
                pyautogui.dragTo(
                    top_x + self.window_bounds.x,
                    self.window_bounds.y + top_y,
                    1
                )
                time.sleep(WaitTime.MEDIUM)
            else:
                # Click on found race
                ClickHandler.click_absolute(
                    int(coord[0]),
                    int(coord[1])
                )
                break

        self.click(self.cfg["lobby_ui"]["race"], WaitTime.SHORT)
        self.click(self.cfg["lobby_ui"]["race_confirm_button"], WaitTime.SHORT)

    def change_race_strategy(self) -> None:
        """Change race strategy if needed for current turn."""
        if self.turn not in self.character.strategy:
            return

        self.strategy = self.character.strategy[self.turn]
        
        coord = self.wait_for_image(
            f"{ImagePath.GENERAL_TRAINING}/ChangeStrategy"
        )
        ClickHandler.click_coordinate(coord)

        coord = self.wait_for_image(
            f"{ImagePath.STRATEGY}/{self.strategy}"
        )
        ClickHandler.click_coordinate(coord)

        coord = self.wait_for_image(
            f"{ImagePath.STRATEGY}/Confirm"
        )
        ClickHandler.click_coordinate(coord)

    def handle_after_race_events(self) -> None:
        """
        Handle events that may occur after a race.

        Raises:
            ContinueException: After handling event.
        """
        while True:
            # Check for trainee event
            try:
                ImageRecognition.identify_image(
                    f"{ImagePath.GENERAL_TRAINING}/TraineeEvent",
                    confidence=ImageConfidence.VERY_HIGH
                )
                coord = ImageRecognition.identify_image(
                    f"{ImagePath.GENERAL_TRAINING}/hi_g"
                )
                ClickHandler.click_coordinate(coord)
                raise ContinueException
            except ImageNotFoundException:
                pass

            # Check for support card event
            try:
                coord = ImageRecognition.identify_image(
                    f"{ImagePath.GENERAL_TRAINING}/SupportCardEvent",
                    confidence=ImageConfidence.VERY_HIGH
                )
                offset_coord = coord.offset(dy=ChoiceOffset.FIRST_CHOICE)
                wait_time = self.cfg["wait_time"]["_check_special_"]
                ClickHandler.click_coordinate(offset_coord, wait_time)
                logger.info(f"Turn {self.turn}: Support card event")
                raise ContinueException
            except ImageNotFoundException:
                pass

            # No more events
            time.sleep(WaitTime.SHORT)

    def check_extra_training_event(self) -> None:
        """Check for and handle extra training event."""
        time.sleep(WaitTime.MEDIUM)
        event_name = self.capture_event_text()

        if event_name == "Extra Training":
            coord = self.wait_for_image(
                f"{ImagePath.GENERAL_TRAINING}/hi_g"
            )
            # Click second option
            offset_coord = coord.offset(dy=81)
            ClickHandler.click_coordinate(offset_coord)
            logger.info(f"Turn {self.turn}: Extra training event")
        else:
            logger.debug(
                f"Turn {self.turn}: No extra training "
                f"(detected: {event_name})"
            )

    def update_support_card_friendship(
        self,
        support_card: SupportCard,
        region: Tuple[int, int, int, int],
        confidence: float = ImageConfidence.VERY_HIGH
    ) -> None:
        """
        Check and update support card friendship status.

        Args:
            support_card: Support card to check.
            region: Screen region where card is located.
            confidence: Confidence threshold for image matching.
        """
        if support_card.friendship:
            return  # Already maxed

        # Check pixel color for orange bar
        r, g, b = pyautogui.pixel(
            int(region[0] + 10),
            int(region[1] + 50)
        )
        
        color_distance = (
            (r - FriendshipColor.ORANGE_R) ** 2 +
            (g - FriendshipColor.ORANGE_G) ** 2 +
            (b - FriendshipColor.ORANGE_B) ** 2
        )

        if color_distance < FriendshipColor.COLOR_THRESHOLD:
            support_card.friendship = 1
            logger.debug(f"Orange bar detected for {support_card}")
            return

        # Check for max friendship icon
        try:
            pyautogui.locateOnScreen(
                f"{ImagePath.BASE_DIR}/{ImagePath.GENERAL_TRAINING}/"
                f"friendship_max.png",
                region=(region[0] - 30, region[1] + 25, 60, 35),
                confidence=confidence
            )
            support_card.friendship = 1
            logger.debug(f"Max friendship detected for {support_card}")
        except ImageNotFoundException:
            logger.debug(
                f"Friendship not maxed for {support_card}: "
                f"{support_card.friendship}"
            )

    def calculate_friendship_bonus(
        self,
        training_type: str,
        support_cards: List[SupportCard]
    ) -> float:
        """
        Calculate friendship bonus for training.

        Args:
            training_type: Type of training.
            support_cards: List of support cards to check.

        Returns:
            Total bonus score.
        """
        cards_to_check = support_cards.copy()
        total_score = 0.0
        participating_cards = []

        for card in cards_to_check:
            coord = ImageRecognition.test_image(
                f"tscard/{card.name}",
                return_coordinate=True
            )
            
            if coord:
                self.update_support_card_friendship(card, region=coord)
                support_cards.remove(card)
                total_score += card.score(training_type, 1)
                participating_cards.append(card.name)

        if participating_cards:
            logger.info(
                f"Turn {self.turn}: Training {training_type} with "
                f"{participating_cards}, bonus: {total_score}"
            )

        return total_score

    def select_best_training(self, mood_score: float) -> None:
        """
        Select and execute best training option.

        Args:
            mood_score: Current mood score.

        Raises:
            ContinueException: After training or mood raising.
        """
        logger.debug(f"Turn {self.turn}: Evaluating training options")

        training_types = [
            TrainingType.SPEED.value,
            TrainingType.STAMINA.value,
            TrainingType.POWER.value,
            TrainingType.GUTS.value,
            TrainingType.WITS.value
        ]
        
        unpresented_cards = list(self.character.supportcard)

        try:
            self.click(self.cfg["root"]["daily_training"]["training"], 2)
            
            # Initialize scores with character priorities plus mood
            scores = self.character.training_priority + [mood_score]
            
            # Avoid clicking same option as previous turn
            check_order = [
                (self.pre_trainoption + i) % 5
                for i in range(1, 6)
            ]

            # Evaluate each training option
            for idx in check_order:
                training_coord = [
                    self.cfg["training_option"]["speed"][0] + 80 * idx,
                    self.cfg["training_option"]["speed"][1]
                ]
                self.click(training_coord, 0)

                # Add friendship bonus
                scores[idx] += self.calculate_friendship_bonus(
                    training_types[idx],
                    unpresented_cards
                )

                # Add NPC bonuses
                if ImageRecognition.test_image(f"{ImagePath.URA}/Director"):
                    scores[idx] += TrainingScore.DIRECTOR_BONUS
                if ImageRecognition.test_image(f"{ImagePath.URA}/Reporter"):
                    scores[idx] += TrainingScore.REPORTER_BONUS

                logger.debug(
                    f"Training option {idx + 1} score: {scores[idx]}"
                )

            # Select best option
            max_index = scores.index(max(scores))

            if max_index == 5:
                # Best option is to raise mood instead
                self.click(self.cfg["root"]["back_button"], 1)
                self.raise_mood()
                self.check_for_date_event()
                raise ContinueException
            else:
                # Execute training
                training_coord = [
                    self.cfg["training_option"]["speed"][0] + max_index * 80,
                    self.cfg["training_option"]["speed"][1]
                ]
                wait_time = self.cfg["wait_time"]["_check_training_"]
                self.click_multiple(training_coord, 4, wait_time)
                
                self.pre_trainoption = max_index
                logger.info(
                    f"Turn {self.turn}: Selected {training_types[max_index]} "
                    f"training, score: {scores[max_index]}"
                )
                
                self.check_extra_training_event()
                raise ContinueException

        except ImageNotFoundException as e:
            logger.error(f"Training selection failed: {e}")

    def execute_ura_training(self) -> None:
        """Execute URA finals training and racing."""
        # Normal training checks
        self.check_for_infirmary()
        self.check_energy_level()
        
        mood_score = MoodScore.GOOD if self.check_mood() else MoodScore.GREAT
        self.select_best_training(mood_score)

        # URA race
        register_wait = self.cfg["wait_time"]["_check_mainrace"]["register"]
        self.click(
            self.cfg["root"]["daily_training"]["race_day"],
            register_wait
        )
        self.click(self.cfg["lobby_ui"]["race_enter"], register_wait)
        
        event_wait = self.cfg["wait_time"]["_check_mainrace"]["event_wait"]
        self.click(self.cfg["lobby_ui"]["race_confirm_button"], event_wait)

        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Result")
        
        result_wait = self.cfg["wait_time"]["_check_mainrace"]["result_button"]
        self.click_multiple(
            self.cfg["lobby_ui"]["view_result_button"],
            3,
            result_wait
        )

    def execute_daily_training(self) -> None:
        """Execute daily training routine."""
        # Check for scheduled race
        self.handle_scheduled_race()

        # Check health
        self.check_for_infirmary()

        # Check for manual race
        manual_race_days = self.event_manage.get("manual_race_day")
        if manual_race_days and self.turn in manual_race_days:
            self.handle_manual_race()
            self.handle_after_race_events()

        # Check energy
        self.check_energy_level()

        # Check mood and train
        mood_score = MoodScore.GOOD if self.check_mood() else MoodScore.GREAT
        self.select_best_training(mood_score)

    def train_horse_loop(
        self,
        name: Optional[str] = None,
        supportcard: Optional[Tuple[SupportCard, ...]] = None,
        style: str = "front",
        turn: int = 1
    ) -> None:
        """
        Main training loop for horse character.

        Args:
            name: Character name (unused).
            supportcard: Support cards (unused).
            style: Racing style.
            turn: Starting turn number.
        """
        self.turn = turn
        self.style = style
        self.pre_trainoption = 0  # Start with speed

        logger.info(f"Starting training loop from turn {turn}")

        while self.turn <= GameTurn.MAX_TURN:
            try:
                if self.turn >= GameTurn.URA_START_TURN:
                    # URA finals
                    logger.info(f"Turn {self.turn}: URA training")
                    self.execute_ura_training()
                elif self.turn in GameTurn.INSPIRATION_TURNS:
                    # Inspiration event
                    logger.info(f"Turn {self.turn}: Inspiration event turn")
                    self.handle_inspiration_event()
                    self.execute_daily_training()
                elif self.turn in GameTurn.NEW_YEAR_TURNS:
                    # New year event
                    logger.info(f"Turn {self.turn}: New year event turn")
                    self.handle_new_year_event()
                    self.execute_daily_training()
                else:
                    # Normal turn
                    self.handle_choice_events()
                    self.execute_daily_training()

            except ContinueException:
                self.turn += 1
                logger.info(f"Advancing to turn {self.turn}")
                time.sleep(WaitTime.MEDIUM)
                continue

        logger.info("Training loop completed")

    def create_manual_setup(
        self,
        support_cards: List[str],
        deck_name: str = "manual"
    ) -> None:
        """
        Create manual setup configuration for support cards.

        Args:
            support_cards: List of support card names.
            deck_name: Name for the configuration file.
        """
        dictionary = {}

        for card in support_cards:
            data = ConfigLoader.load_support_card_data(card)
            dictionary[card] = {}

            for key, value in data.items():
                options = value.get("options")
                if options is None or len(options) == 1:
                    dictionary[card][key] = "Auto"
                else:
                    dictionary[card][key] = 0

        dictionary["manual_race_day"] = []
        dictionary["race_day"] = []

        output_path = Path(f"data/json/{deck_name}.json")
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)

        logger.info(f"Manual setup created: {output_path}")


def resize_game(window_title: str = GameWindow.TITLE) -> None:
    """
    Resize game window to standard dimensions.

    Args:
        window_title: Title of the game window.
    """
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        WindowManager.resize_window(window, GameWindow.TARGET_WIDTH)
        logger.info(f"Resized window '{window_title}'")
    except (IndexError, Exception) as e:
        logger.error(f"Failed to resize window: {e}")


def main() -> None:
    """Main entry point."""
    try:
        resize_game()
        
        game = UmaGame(test=True)
        # game._start_game(1)  # Method not implemented
        # game.train_horse_loop(turn=1)
        
    except Exception as e:
        logger.error(f"Game automation failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
