"""
Main game controller for Umamusume automation.

This is the refactored main control file with a clean, modular structure.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Union

from core import (
    GameWindow,
    GameTurn,
    WaitTime,
    ImagePath,
    MoodScore,
    Coordinate,
    ContinueException,
    WindowBounds,
)
from config.paths import Paths
from ui import ImageRecognition, ClickHandler, WindowManager
from game_utils import ConfigLoader
from game_utils.screen_reader import GameScreenReader
from events import (
    EventHandlers,
    MoodManager,
    HealthManager,
    RaceManager,
    TrainingManager,
)
from horse_info import HorseGirl, El_Condor
from shared.utils.logger import Logger

logger = Logger.get_logger()


class UmaGame:
    """Main game automation controller."""

    def __init__(
        self,
        support_card: Optional[Tuple] = None,
        race_day: Optional[List[int]] = None,
        manual_race_day: Optional[List[int]] = None,
        test: bool = True,
        deck_name: str = "Cap",
        character: HorseGirl = El_Condor,
    ):
        """
        Initialize the game controller.

        Args:
            support_card: Tuple of support cards (unused).
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

        # Configuration
        self.cfg = ConfigLoader.load_dictionary()
        self.event_manage = ConfigLoader.load_deck_config(deck_name)
        self.list_event = self._setup_event_dictionary(self.event_manage)

        # Window setup
        self.window_bounds = WindowManager.setup_game_window()

        # Screen reader
        self.screen_reader = GameScreenReader(self.window_bounds)

    def _setup_event_dictionary(
        self, event_manage: Optional[Dict[str, Any]]
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
        return Coordinate(self.window_bounds.x + x, self.window_bounds.y + y)

    def click(
        self, coord: Tuple[float, float], interval: float = WaitTime.SHORT
    ) -> None:
        """
        Click at game-relative coordinates.

        Args:
            coord: Coordinates relative to game window.
            interval: Wait time after click.
        """
        abs_coord = self._relative_to_absolute(coord)
        ClickHandler.click_coordinate(abs_coord, interval)

    def click_multiple(
        self, coord: Tuple[float, float], count: int, interval: float = WaitTime.SHORT
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

        abs_coord = self._relative_to_absolute(coord)
        for _ in range(count):
            ClickHandler.click_coordinate(abs_coord, interval)

    def wait_for_image(
        self,
        image_path: str,
        confidence: float = 0.8,
        check_interval: float = WaitTime.SHORT,
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
                coord = ImageRecognition.find_image_center(
                    image_path, confidence=confidence
                )
                return coord
            except Exception:
                time.sleep(check_interval)

    def confirm_goal_completion(self) -> None:
        """Confirm goal completion after race."""
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Next")
        self.click(self.cfg["lobby_ui"]["next_button"])
        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Next")
        self.click(self.cfg["lobby_ui"]["next_button"])

    def execute_ura_training(self) -> None:
        """Execute URA finals training and racing."""
        # Normal training checks
        HealthManager.check_for_infirmary(self.click, self.cfg, self.turn)
        HealthManager.check_energy_level(self.click, self.cfg, self.turn)

        mood_score = (
            MoodScore.GOOD
            if MoodManager.check_mood(
                self.turn,
                lambda: MoodManager.raise_mood(self.click, self.cfg, self.turn),
                lambda: EventHandlers.check_for_date_event(
                    EventHandlers.detect_event_type,
                    lambda c: EventHandlers.handle_special_event(
                        c, self.list_event, self.cfg, self.screen_reader, self.turn
                    ),
                    self.turn,
                ),
            )
            else MoodScore.GREAT
        )

        TrainingManager.select_best_training(
            self.turn,
            mood_score,
            self.character,
            self.click,
            self.click_multiple,
            lambda: MoodManager.raise_mood(self.click, self.cfg, self.turn),
            lambda: EventHandlers.check_for_date_event(
                EventHandlers.detect_event_type,
                lambda c: EventHandlers.handle_special_event(
                    c, self.list_event, self.cfg, self.screen_reader, self.turn
                ),
                self.turn,
            ),
            lambda: EventHandlers.check_extra_training_event(
                self.wait_for_image,
                lambda: self.screen_reader.capture_event_text(
                    self.screen_reader.get_event_text_region(self.cfg)
                ),
                self.turn,
            ),
            self.cfg,
        )

        # URA race
        register_wait = self.cfg["wait_time"]["_check_mainrace"]["register"]
        self.click(self.cfg["root"]["daily_training"]["race_day"], register_wait)
        self.click(self.cfg["lobby_ui"]["race_enter"], register_wait)

        event_wait = self.cfg["wait_time"]["_check_mainrace"]["event_wait"]
        self.click(self.cfg["lobby_ui"]["race_confirm_button"], event_wait)

        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Result")

        result_wait = self.cfg["wait_time"]["_check_mainrace"]["result_button"]
        self.click_multiple(self.cfg["lobby_ui"]["view_result_button"], 3, result_wait)

    def execute_daily_training(self) -> None:
        """Execute daily training routine."""
        # Check for manual race
        manual_race_days = self.event_manage.get("manual_race_day")
        if manual_race_days and self.turn in manual_race_days:
            self.handle_manual_race()
            EventHandlers.handle_after_race_events(
                self.wait_for_image, self.cfg, self.turn
            )
        # Check for scheduled race
        RaceManager.handle_scheduled_race(
            self.turn,
            self.event_manage.get("race_day", []),
            lambda: RaceManager.upgrade_skills(
                self.window_bounds,
                self.wait_for_image,
                self.click,
                self.screen_reader,
                self.cfg,
            ),
            self.wait_for_image,
            self.click,
            self.click_multiple,
            self.confirm_goal_completion,
            self.cfg,
        )

        # Check health
        HealthManager.check_for_infirmary(self.click, self.cfg, self.turn)

        

        # Check energy
        HealthManager.check_energy_level(self.click, self.cfg, self.turn)

        # Check mood and train
        mood_score = (
            MoodScore.GOOD
            if MoodManager.check_mood(
                self.turn,
                lambda: MoodManager.raise_mood(self.click, self.cfg, self.turn),
                lambda: EventHandlers.check_for_date_event(
                    EventHandlers.detect_event_type,
                    lambda c: EventHandlers.handle_special_event(
                        c, self.list_event, self.cfg, self.screen_reader, self.turn
                    ),
                    self.turn,
                ),
            )
            else MoodScore.GREAT
        )

        TrainingManager.select_best_training(
            self.turn,
            mood_score,
            self.character,
            self.click,
            self.click_multiple,
            lambda: MoodManager.raise_mood(self.click, self.cfg, self.turn),
            lambda: EventHandlers.check_for_date_event(
                EventHandlers.detect_event_type,
                lambda c: EventHandlers.handle_special_event(
                    c, self.list_event, self.cfg, self.screen_reader, self.turn
                ),
                self.turn,
            ),
            lambda: EventHandlers.check_extra_training_event(
                self.wait_for_image,
                lambda: self.screen_reader.capture_event_text(
                    self.screen_reader.get_event_text_region(self.cfg)
                ),
                self.turn,
            ),
            self.cfg,
        )

    def handle_manual_race(self) -> None:
        """Handle manually scheduled race."""
        logger.info(f"Turn {self.turn}: Manual race scheduled")

        # wait_time = self.cfg["wait_time"]["_check_mainrace"]["register"]
        # self.click(self.cfg["root"]["daily_training"]["race_day"], wait_time)

        wait_time = self.cfg["wait_time"]["_check_mainrace"]["register"]
        coord = self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Race1")
        ClickHandler.click_coordinate(coord, wait_time)

        try:
            coord = ImageRecognition.find_image_center (f"{ImagePath.GENERAL_TRAINING}/OK")
            ClickHandler.click_coordinate(coord, wait_time)
        except Exception:
            pass
        

        # RaceManager.find_race(
        #     self.turn,
        #     self.event_manage["race_table"],
        #     self.window_bounds,
        #     self.click,
        #     self.cfg,
        # )

        self.click(self.cfg["lobby_ui"]["race_enter"], wait_time)

        event_wait = self.cfg["wait_time"]["_check_mainrace"]["event_wait"]
        self.click(self.cfg["lobby_ui"]["race_confirm_button"], event_wait)

        RaceManager.change_race_strategy(self.turn, self.character, self.wait_for_image)

        self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/Result")

        result_wait = self.cfg["wait_time"]["_check_mainrace"]["result_button"]
        self.click_multiple(self.cfg["lobby_ui"]["view_result_button"], 3, result_wait)

        coord = self.wait_for_image(f"{ImagePath.GENERAL_TRAINING}/NextRace")
        ClickHandler.click_coordinate(coord)
        logger.info(f"Turn {self.turn}: Manual race completed")


    def train_horse_loop(
        self,
        name: Optional[str] = None,
        supportcard: Optional[Tuple] = None,
        style: str = "front",
        turn: int = 1,
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
                    EventHandlers.handle_inspiration_event(self.cfg, self.turn)
                    self.execute_daily_training()
                elif self.turn in GameTurn.NEW_YEAR_TURNS:
                    # New year event
                    logger.info(f"Turn {self.turn}: New year event turn")
                    EventHandlers.handle_new_year_event(
                        self.wait_for_image, self.cfg, self.turn
                    )
                    self.execute_daily_training()
                else:
                    # Normal turn
                    coord, event_type = EventHandlers.detect_event_type()
                    if coord:
                        EventHandlers.handle_special_event(
                            coord,
                            self.list_event,
                            self.cfg,
                            self.screen_reader,
                            self.turn,
                        )
                    self.execute_daily_training()

            except ContinueException:
                self.turn += 1
                logger.info(f"Advancing to turn {self.turn}")
                time.sleep(WaitTime.LONG)
                continue

        logger.info("Training loop completed")

    def create_manual_setup(
        self, support_cards: List[str], deck_name: str = "manual"
    ) -> None:
        """
        Create manual setup configuration for support cards.

        Args:
            support_cards: List of support card names.
            deck_name: Name for the configuration file.
        """
        dictionary = {}

        for card in support_cards:
            data = ConfigLoader.load_support_card_event(card)
            dictionary[card] = {}

            for key, value in data.items():
                options = value.get("options")
                if options is None or len(options) == 1:
                    dictionary[card][key] = "Auto"
                else:
                    dictionary[card][key] = 0

        dictionary["manual_race_day"] = []
        dictionary["race_day"] = []

        output_path = Paths.MANUAL_SETUP_EVENT_DIR / f"{deck_name}.json"
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
        window = WindowManager.get_game_window()
        WindowManager.resize_window(window, GameWindow.TARGET_WIDTH)
        logger.info(f"Resized window '{window_title}'")
    except Exception as e:
        logger.error(f"Failed to resize window: {e}")


def main() -> None:
    """Main entry point."""
    try:
        resize_game()

        game = UmaGame(test=True)
        game.train_horse_loop(turn=1)

    except Exception as e:
        logger.error(f"Game automation failed: {e}", exc_info=True)
        raise


# if __name__ == "__main__":
#     main()
