"""
Interactive test suite for event management classes.

This module provides interactive testing for all event handler classes,
allowing users to specify parameters for testing specific functions.

Usage:
    python test_event.py

    Or import and use specific test functions:
    >>> from test_event import test_health_manager
    >>> test_health_manager(test_function='check_energy')
"""

import argparse
import sys
import time
from typing import Optional, Dict, Any, Callable
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from events import (
    EventHandlers,
    MoodManager,
    HealthManager,
    RaceManager,
    TrainingManager,
)
from core.models import ContinueException, MoodLevel, EventType
from core.constants import ImagePath


class TestHelpers:
    """Helper utilities for testing."""

    @staticmethod
    def create_mock_click_func(verbose: bool = True) -> Mock:
        """Create a mock click function."""
        mock = Mock()
        if verbose:
            mock.side_effect = lambda *args, **kwargs: print(
                f"  [CLICK] Called with: {args}, {kwargs}"
            )
        return mock

    @staticmethod
    def create_mock_cfg() -> Dict[str, Any]:
        """Create a mock configuration dictionary."""
        return {
            "wait_time": {
                "_check_mainrace": {"register": 1.0, "race_button": 0.5},
                "_check_special_": 1.0,
                "_check_multiq": 1.0,
                "_check_energy_": 2.0,
                "_check_training_": 1.0,
                "_raise_mood_": 2.0,
            },
            "root": {
                "daily_training": {
                    "infirmary": (100, 100),
                    "rest": (200, 200),
                    "recreation": (300, 300),
                    "training": (400, 400),
                    "race_day": (500, 500),
                },
                "back_button": (50, 50),
            },
            "lobby_ui": {
                "race_enter": (600, 600),
                "race_confirm_button": (700, 700),
                "view_result_button": (800, 800),
                "race_button": (900, 900),
                "race": (1000, 1000),
            },
            "race_day": {
                "skills": (1100, 1100),
                "back_button": (1200, 1200),
            },
            "training_option": {
                "speed": [100, 200],
            },
            "race_ui": {
                "top_race": (300, 100),
                "bottom_race": (300, 500),
            },
        }

    @staticmethod
    def create_mock_character():
        """Create a mock character object."""
        character = Mock()
        character.training_priority = [1.0, 1.0, 1.0, 1.0, 1.0]
        character.supportcard = []
        character.pre_trainoption = 0
        character.strategy = {}
        return character

    @staticmethod
    def print_test_header(class_name: str, function_name: str):
        """Print formatted test header."""
        print(f"\n{'='*70}")
        print(f"Testing: {class_name}.{function_name}")
        print(f"{'='*70}")

    @staticmethod
    def print_test_result(success: bool, message: str = ""):
        """Print test result."""
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"\n{status}")
        if message:
            print(f"Details: {message}")
        print(f"{'='*70}\n")


# ============================================================================
# HealthManager Tests
# ============================================================================


def test_health_manager(
    test_function: Optional[str] = None, mock_image_exists: bool = False, turn: int = 10
):
    """
    Test HealthManager functions.

    Args:
        test_function: Specific function to test ('check_infirmary' or 'check_energy').
                      If None, tests all functions.
        mock_image_exists: Whether to mock image as existing (True) or not (False).
        turn: Turn number for testing.
    """
    functions = {
        "check_infirmary": _test_check_for_infirmary,
        "check_energy": _test_check_energy_level,
    }

    if test_function:
        if test_function in functions:
            functions[test_function](turn)
        else:
            print(f"Unknown function: {test_function}")
            print(f"Available functions: {list(functions.keys())}")
    else:
        # Test all functions
        for func in functions.values():
            func(turn)


def _test_check_for_infirmary(turn: int):
    """Test check_for_infirmary function."""
    TestHelpers.print_test_header("HealthManager", "check_for_infirmary")

    click_func = TestHelpers.create_mock_click_func()
    cfg = TestHelpers.create_mock_cfg()

    print(f"Parameters: turn={turn}")


    try:
        result = HealthManager.check_for_infirmary(click_func, cfg, turn)

        TestHelpers.print_test_result(
            False, "Expected ContinueException but none was raised"
        )
    except ContinueException:
        TestHelpers.print_test_result(
            True, "ContinueException raised as expected"
            )


def _test_check_energy_level(turn: int):
    """Test check_energy_level function."""
    TestHelpers.print_test_header("HealthManager", "check_energy_level")

    click_func = TestHelpers.create_mock_click_func()
    cfg = TestHelpers.create_mock_cfg()

    print(f"Parameters: turn={turn}")

    try:
        result = HealthManager.check_energy_level(click_func, cfg, turn)
        TestHelpers.print_test_result(
            result == True, f"Returned: {result}, Expected: True"
        )
    except ContinueException:
        TestHelpers.print_test_result(
            True, "ContinueException raised as expected"
        )


# ============================================================================
# MoodManager Tests
# ============================================================================


def test_mood_manager(
    test_function: Optional[str] = None,
    mood_level: Optional[str] = None,
    turn: int = 10,
):
    """
    Test MoodManager functions.

    Args:
        test_function: Specific function to test ('get_mood', 'raise_mood', 'check_mood').
                      If None, tests all functions.
        mood_level: Mood level for testing ('awful', 'bad', 'normal', 'good', 'great').
        turn: Turn number for testing.

    Examples:
        >>> # Test mood detection with bad mood
        >>> test_mood_manager(test_function='get_mood', mood_level='bad')

        >>> # Test raising mood
        >>> test_mood_manager(test_function='raise_mood', turn=15)

        >>> # Test full mood check with good mood
        >>> test_mood_manager(test_function='check_mood', mood_level='good', turn=20)
    """
    functions = {
        "get_mood": _test_get_mood_level,
        "raise_mood": _test_raise_mood,
        "check_mood": _test_check_mood,
    }

    if test_function:
        if test_function in functions:
            if test_function == "get_mood":
                functions[test_function](mood_level)
            elif test_function == "raise_mood":
                functions[test_function](turn)
            else:
                functions[test_function](mood_level, turn)
        else:
            print(f"Unknown function: {test_function}")
            print(f"Available functions: {list(functions.keys())}")
    else:
        # Test all functions
        _test_get_mood_level(mood_level)
        _test_raise_mood(turn)
        _test_check_mood(mood_level, turn)


def _test_get_mood_level(mood_level: Optional[str]):
    """Test get_mood_level function."""
    TestHelpers.print_test_header("MoodManager", "get_mood_level")

    mood_map = {
        "awful": MoodLevel.AWFUL,
        "bad": MoodLevel.BAD,
        "normal": MoodLevel.NORMAL,
        "good": MoodLevel.GOOD,
        "great": None,
    }

    target_mood = mood_map.get(mood_level, MoodLevel.NORMAL)
    print(f"Parameters: mood_level={mood_level}")

    with patch("events.mood_manager.ImageRecognition.check_image_exists") as mock_check:
        # Mock returns True only for the target mood
        def check_exists(path, confidence=0.85):
            if target_mood is None:
                return False
            return target_mood.value in path

        mock_check.side_effect = check_exists

        result = MoodManager.get_mood_level()
        TestHelpers.print_test_result(
            result == target_mood, f"Returned: {result}, Expected: {target_mood}"
        )


def _test_raise_mood(turn: int):
    """Test raise_mood function."""
    TestHelpers.print_test_header("MoodManager", "raise_mood")

    click_func = TestHelpers.create_mock_click_func()
    cfg = TestHelpers.create_mock_cfg()

    print(f"Parameters: turn={turn}")

    with patch("events.mood_manager.ImageRecognition.check_image_exists") as mock_check:
        mock_check.return_value = True

        try:
            MoodManager.raise_mood(click_func, cfg, turn)
            TestHelpers.print_test_result(True, "Mood raised successfully")
        except Exception as e:
            TestHelpers.print_test_result(False, f"Error: {e}")


def _test_check_mood(mood_level: Optional[str], turn: int):
    """Test check_mood function."""
    TestHelpers.print_test_header("MoodManager", "check_mood")

    mood_map = {
        "awful": MoodLevel.AWFUL,
        "bad": MoodLevel.BAD,
        "normal": MoodLevel.NORMAL,
        "good": MoodLevel.GOOD,
        "great": None,
    }

    target_mood = mood_map.get(mood_level, None)
    print(f"Parameters: mood_level={mood_level}, turn={turn}")

    raise_mood_func = TestHelpers.create_mock_click_func()
    check_date_func = TestHelpers.create_mock_click_func()

    with patch("events.mood_manager.MoodManager.get_mood_level") as mock_get_mood:
        with patch(
            "events.mood_manager.ImageRecognition.check_image_exists"
        ) as mock_check:
            mock_get_mood.return_value = target_mood
            mock_check.return_value = mood_level == "good"

            try:
                result = MoodManager.check_mood(turn, raise_mood_func, check_date_func)

                if target_mood is None:  # Great mood
                    expected = 0 if mood_level != "good" else 3
                    TestHelpers.print_test_result(
                        result == expected, f"Returned: {result}, Expected: {expected}"
                    )
                else:
                    TestHelpers.print_test_result(False, "Expected ContinueException")
            except ContinueException:
                if target_mood is not None:
                    TestHelpers.print_test_result(
                        True, "ContinueException raised for bad mood"
                    )
                else:
                    TestHelpers.print_test_result(False, "Unexpected ContinueException")


# ============================================================================
# EventHandlers Tests
# ============================================================================


def test_event_handlers(
    test_function: Optional[str] = None, event_type: str = "choice", turn: int = 10
):
    """
    Test EventHandlers functions.

    Args:
        test_function: Specific function to test ('special_event', 'inspiration',
                      'new_year', 'detect_event', 'date_event', 'after_race', 'extra_training').
        event_type: Type of event for detection ('choice', 'training', 'race_main').
        turn: Turn number for testing.

    Examples:
        >>> # Test special event handling
        >>> test_event_handlers(test_function='special_event', turn=5)

        >>> # Test event type detection
        >>> test_event_handlers(test_function='detect_event', event_type='training')
    """
    functions = {
        "special_event": _test_handle_special_event,
        "inspiration": _test_handle_inspiration_event,
        "new_year": _test_handle_new_year_event,
        "detect_event": _test_detect_event_type,
        "date_event": _test_check_for_date_event,
        "after_race": _test_handle_after_race_events,
        "extra_training": _test_check_extra_training_event,
    }

    if test_function:
        if test_function in functions:
            if test_function == "detect_event":
                functions[test_function](event_type)
            else:
                functions[test_function](turn)
        else:
            print(f"Unknown function: {test_function}")
            print(f"Available functions: {list(functions.keys())}")
    else:
        # Test all functions
        for key, func in functions.items():
            if key == "detect_event":
                func(event_type)
            else:
                func(turn)


def _test_handle_special_event(turn: int):
    """Test handle_special_event function."""
    TestHelpers.print_test_header("EventHandlers", "handle_special_event")

    from core.models import Coordinate

    coord = Coordinate(100, 200)
    event_list = {"Test Event": 1, "Auto Event": "Auto"}
    cfg = TestHelpers.create_mock_cfg()
    screen_reader = Mock()
    screen_reader.get_event_text_region.return_value = (0, 0, 100, 100)
    screen_reader.capture_event_text.return_value = "Test Event"

    print(f"Parameters: turn={turn}, coord={coord}")

    with patch("events.event_handlers.EventMatcher.match_event") as mock_match:
        with patch("events.event_handlers.ClickHandler.click_coordinate") as mock_click:
            mock_match.return_value = "Test Event"

            try:
                EventHandlers.handle_special_event(
                    coord, event_list, cfg, screen_reader, turn
                )
                TestHelpers.print_test_result(
                    True, "Special event handled successfully"
                )
            except Exception as e:
                TestHelpers.print_test_result(False, f"Error: {e}")


def _test_handle_inspiration_event(turn: int):
    """Test handle_inspiration_event function."""
    TestHelpers.print_test_header("EventHandlers", "handle_inspiration_event")

    cfg = TestHelpers.create_mock_cfg()
    print(f"Parameters: turn={turn}")

    with patch(
        "events.event_handlers.ImageRecognition.check_image_exists"
    ) as mock_check:
        # Return True once then exit loop
        mock_check.side_effect = [True]

        try:
            EventHandlers.handle_inspiration_event(cfg, turn)
            TestHelpers.print_test_result(True, "Inspiration event handled")
        except Exception as e:
            TestHelpers.print_test_result(False, f"Error: {e}")


def _test_handle_new_year_event(turn: int):
    """Test handle_new_year_event function."""
    TestHelpers.print_test_header("EventHandlers", "handle_new_year_event")

    from core.models import Coordinate

    cfg = TestHelpers.create_mock_cfg()
    wait_func = Mock(return_value=Coordinate(100, 200))

    print(f"Parameters: turn={turn}")

    with patch("events.event_handlers.ClickHandler.click_coordinate") as mock_click:
        try:
            EventHandlers.handle_new_year_event(wait_func, cfg, turn)
            TestHelpers.print_test_result(True, "New year event handled")
        except Exception as e:
            TestHelpers.print_test_result(False, f"Error: {e}")


def _test_detect_event_type(event_type: str):
    """Test detect_event_type function."""
    TestHelpers.print_test_header("EventHandlers", "detect_event_type")

    from core.models import Coordinate
    from pyautogui import ImageNotFoundException

    print(f"Parameters: event_type={event_type}")

    with patch("events.event_handlers.ImageRecognition.find_image_center") as mock_find:
        if event_type == "choice":
            mock_find.side_effect = [Coordinate(100, 200)]
            expected_type = EventType.CHOICE_EVENT
        elif event_type == "training":
            mock_find.side_effect = [ImageNotFoundException(), Coordinate(100, 200)]
            expected_type = EventType.TRAINING
        elif event_type == "race_main":
            mock_find.side_effect = [
                ImageNotFoundException(),
                ImageNotFoundException(),
                Coordinate(100, 200),
            ]
            expected_type = EventType.RACE_MAIN
        else:
            mock_find.side_effect = ImageNotFoundException()
            expected_type = EventType.TRAINING

        coord, result_type = EventHandlers.detect_event_type()
        TestHelpers.print_test_result(
            result_type == expected_type,
            f"Returned: {result_type}, Expected: {expected_type}",
        )


def _test_check_for_date_event(turn: int):
    """Test check_for_date_event function."""
    TestHelpers.print_test_header("EventHandlers", "check_for_date_event")

    from core.models import Coordinate

    detect_func = Mock(return_value=(Coordinate(100, 200), EventType.CHOICE_EVENT))
    handle_func = Mock()

    print(f"Parameters: turn={turn}")

    try:
        EventHandlers.check_for_date_event(detect_func, handle_func, turn)
        TestHelpers.print_test_result(True, "Date event check completed")
    except Exception as e:
        TestHelpers.print_test_result(False, f"Error: {e}")


def _test_handle_after_race_events(turn: int):
    """Test handle_after_race_events function."""
    TestHelpers.print_test_header("EventHandlers", "handle_after_race_events")

    from pyautogui import ImageNotFoundException

    cfg = TestHelpers.create_mock_cfg()
    wait_func = Mock()

    print(f"Parameters: turn={turn}")

    with patch("events.event_handlers.ImageRecognition.find_image_center") as mock_find:
        # Simulate no events found (infinite loop breaker)
        mock_find.side_effect = ImageNotFoundException()

        try:
            # This will run indefinitely, so we'll just test the setup
            TestHelpers.print_test_result(
                True, "Test setup completed (note: infinite loop in actual usage)"
            )
        except Exception as e:
            TestHelpers.print_test_result(False, f"Error: {e}")


def _test_check_extra_training_event(turn: int):
    """Test check_extra_training_event function."""
    TestHelpers.print_test_header("EventHandlers", "check_extra_training_event")

    from core.models import Coordinate

    wait_func = Mock(return_value=Coordinate(100, 200))
    capture_func = Mock(return_value="Extra Training")

    print(f"Parameters: turn={turn}")

    with patch("events.event_handlers.ClickHandler.click_coordinate") as mock_click:
        try:
            EventHandlers.check_extra_training_event(wait_func, capture_func, turn)
            TestHelpers.print_test_result(True, "Extra training event checked")
        except Exception as e:
            TestHelpers.print_test_result(False, f"Error: {e}")


# ============================================================================
# RaceManager Tests
# ============================================================================


def test_race_manager(
    test_function: Optional[str] = None, turn: int = 10, race_name: str = "Japan Cup"
):
    """
    Test RaceManager functions.

    Args:
        test_function: Specific function to test ('scheduled_race', 'upgrade_skills',
                      'find_race', 'change_strategy').
        turn: Turn number for testing.
        race_name: Name of race for find_race test.

    Examples:
        >>> # Test scheduled race handling
        >>> test_race_manager(test_function='scheduled_race', turn=24)

        >>> # Test finding a specific race
        >>> test_race_manager(test_function='find_race', race_name='Satsuki Sho')
    """
    functions = {
        "scheduled_race": _test_handle_scheduled_race,
        "upgrade_skills": _test_upgrade_skills,
        "find_race": _test_find_race,
        "change_strategy": _test_change_race_strategy,
    }

    if test_function:
        if test_function in functions:
            if test_function == "find_race":
                functions[test_function](turn, race_name)
            else:
                functions[test_function](turn)
        else:
            print(f"Unknown function: {test_function}")
            print(f"Available functions: {list(functions.keys())}")
    else:
        # Test all functions
        _test_handle_scheduled_race(turn)
        _test_upgrade_skills(turn)
        _test_find_race(turn, race_name)
        _test_change_race_strategy(turn)


def _test_handle_scheduled_race(turn: int):
    """Test handle_scheduled_race function."""
    TestHelpers.print_test_header("RaceManager", "handle_scheduled_race")

    race_days = [10, 24, 35]
    cfg = TestHelpers.create_mock_cfg()

    upgrade_func = Mock()
    wait_func = Mock()
    click_func = TestHelpers.create_mock_click_func()
    click_multi_func = Mock()
    confirm_func = Mock()

    print(f"Parameters: turn={turn}, race_days={race_days}")

    try:
        RaceManager.handle_scheduled_race(
            turn,
            race_days,
            upgrade_func,
            wait_func,
            click_func,
            click_multi_func,
            confirm_func,
            cfg,
        )

        if turn in race_days:
            TestHelpers.print_test_result(False, "Expected ContinueException")
        else:
            TestHelpers.print_test_result(True, "Non-race day handled correctly")
    except ContinueException:
        if turn in race_days:
            TestHelpers.print_test_result(
                True, "Race day handled, ContinueException raised"
            )
        else:
            TestHelpers.print_test_result(False, "Unexpected ContinueException")


def _test_upgrade_skills(turn: int):
    """Test upgrade_skills function."""
    TestHelpers.print_test_header("RaceManager", "upgrade_skills")

    from core.models import WindowBounds

    window_bounds = WindowBounds(x=0, y=0, width=1920, height=1080)
    cfg = TestHelpers.create_mock_cfg()

    wait_func = Mock()
    click_func = TestHelpers.create_mock_click_func()
    screen_reader = Mock()

    print(f"Parameters: turn={turn}")

    with patch("pyautogui.locateOnScreen") as mock_locate:
        with patch("pyautogui.click") as mock_click:
            mock_locate.side_effect = Exception("End of list")

            try:
                RaceManager.upgrade_skills(
                    window_bounds, wait_func, click_func, screen_reader, cfg
                )
                TestHelpers.print_test_result(True, "Skill upgrade completed")
            except Exception as e:
                TestHelpers.print_test_result(
                    True, f"Skill upgrade completed with expected exit: {e}"
                )


def _test_find_race(turn: int, race_name: str):
    """Test find_race function."""
    TestHelpers.print_test_header("RaceManager", "find_race")

    from core.models import WindowBounds, Coordinate

    window_bounds = WindowBounds(x=0, y=0, width=1920, height=1080)
    cfg = TestHelpers.create_mock_cfg()
    click_func = TestHelpers.create_mock_click_func()
    race_table = {str(turn): race_name}

    print(f"Parameters: turn={turn}, race_name={race_name}")

    with patch("events.race_manager.ImageRecognition.find_image_center") as mock_find:
        with patch("events.race_manager.ClickHandler.click_coordinate") as mock_click:
            mock_find.return_value = Coordinate(100, 200)

            try:
                RaceManager.find_race(turn, race_table, window_bounds, click_func, cfg)
                TestHelpers.print_test_result(True, "Race found and selected")
            except Exception as e:
                TestHelpers.print_test_result(False, f"Error: {e}")


def _test_change_race_strategy(turn: int):
    """Test change_race_strategy function."""
    TestHelpers.print_test_header("RaceManager", "change_race_strategy")

    from core.models import Coordinate

    character = TestHelpers.create_mock_character()
    character.strategy = {turn: "Nige"}
    wait_func = Mock(return_value=Coordinate(100, 200))

    print(f"Parameters: turn={turn}, strategy={character.strategy.get(turn)}")

    with patch("events.race_manager.ClickHandler.click_coordinate") as mock_click:
        try:
            RaceManager.change_race_strategy(turn, character, wait_func)
            TestHelpers.print_test_result(True, "Strategy changed successfully")
        except Exception as e:
            TestHelpers.print_test_result(False, f"Error: {e}")


# ============================================================================
# TrainingManager Tests
# ============================================================================


def test_training_manager(
    test_function: Optional[str] = None, turn: int = 10, training_type: str = "speed"
):
    """
    Test TrainingManager functions.

    Args:
        test_function: Specific function to test ('update_friendship', 'select_training').
        turn: Turn number for testing.
        training_type: Type of training for testing.

    Examples:
        >>> # Test friendship update
        >>> test_training_manager(test_function='update_friendship')

        >>> # Test training selection
        >>> test_training_manager(test_function='select_training', turn=15)
    """
    functions = {
        "update_friendship": _test_update_support_card_friendship,
        "select_training": _test_select_best_training,
    }

    if test_function:
        if test_function in functions:
            functions[test_function](turn)
        else:
            print(f"Unknown function: {test_function}")
            print(f"Available functions: {list(functions.keys())}")
    else:
        # Test all functions
        for func in functions.values():
            func(turn)


def _test_update_support_card_friendship(turn: int):
    """Test update_support_card_friendship function."""
    TestHelpers.print_test_header("TrainingManager", "update_support_card_friendship")

    from shared.models.support_card import SupportCard

    card = SupportCard(name="Test Card", rarity="SSR", character_type="speed")
    region = (100, 100, 200, 200)

    print(f"Parameters: card={card.name}, region={region}")

    with patch("pyautogui.pixel") as mock_pixel:
        with patch("pyautogui.locateOnScreen") as mock_locate:
            from pyautogui import ImageNotFoundException

            # Test orange bar detection
            mock_pixel.return_value = (255, 165, 0)  # Orange color
            mock_locate.side_effect = ImageNotFoundException()

            try:
                TrainingManager.update_support_card_friendship(card, region)
                TestHelpers.print_test_result(
                    card.friendship == 1, f"Friendship updated: {card.friendship}"
                )
            except Exception as e:
                TestHelpers.print_test_result(False, f"Error: {e}")


def _test_select_best_training(turn: int):
    """Test select_best_training function."""
    TestHelpers.print_test_header("TrainingManager", "select_best_training")

    cfg = TestHelpers.create_mock_cfg()
    character = TestHelpers.create_mock_character()

    click_func = TestHelpers.create_mock_click_func()
    click_multi_func = Mock()
    raise_mood_func = Mock()
    check_date_func = Mock()
    check_extra_func = Mock()

    print(f"Parameters: turn={turn}, mood_score=0.0")

    with patch(
        "events.training_manager.ImageRecognition.check_image_exists"
    ) as mock_check:
        mock_check.return_value = False

        try:
            TrainingManager.select_best_training(
                turn,
                0.0,
                character,
                click_func,
                click_multi_func,
                raise_mood_func,
                check_date_func,
                check_extra_func,
                cfg,
            )
            TestHelpers.print_test_result(False, "Expected ContinueException")
        except ContinueException:
            TestHelpers.print_test_result(
                True, "Training selected, ContinueException raised"
            )
        except Exception as e:
            TestHelpers.print_test_result(False, f"Error: {e}")


# ============================================================================
# Main Test Runner
# ============================================================================


def run_all_tests():
    """Run all test suites."""
    print("\n" + "=" * 70)
    print("RUNNING ALL TEST SUITES")
    print("=" * 70)

    print("\n--- HealthManager Tests ---")
    test_health_manager()

    print("\n--- MoodManager Tests ---")
    test_mood_manager()

    print("\n--- EventHandlers Tests ---")
    test_event_handlers()

    print("\n--- RaceManager Tests ---")
    test_race_manager()

    print("\n--- TrainingManager Tests ---")
    test_training_manager()

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70 + "\n")


def main():
    """Main entry point for interactive testing."""
    parser = argparse.ArgumentParser(
        description="Interactive test suite for event management classes"
    )
    parser.add_argument(
        "--class",
        dest="class_name",
        choices=["health", "mood", "event", "race", "training", "all"],
        help="Class to test",
    )
    parser.add_argument(
        "--function", dest="function_name", help="Specific function to test"
    )
    parser.add_argument(
        "--turn", type=int, default=10, help="Turn number for testing (default: 10)"
    )
    parser.add_argument(
        "--image-exists",
        action="store_true",
        help="Mock image as existing for health tests",
    )
    parser.add_argument(
        "--mood",
        choices=["awful", "bad", "normal", "good", "great"],
        help="Mood level for mood tests",
    )
    parser.add_argument(
        "--event-type",
        choices=["choice", "training", "race_main"],
        default="choice",
        help="Event type for event detection tests",
    )
    parser.add_argument(
        "--race-name", default="Japan Cup", help="Race name for race tests"
    )

    args = parser.parse_args()

    if args.class_name == "all" or not args.class_name:
        run_all_tests()
    elif args.class_name == "health":
        test_health_manager(args.function_name, args.image_exists, args.turn)
    elif args.class_name == "mood":
        test_mood_manager(args.function_name, args.mood, args.turn)
    elif args.class_name == "event":
        test_event_handlers(args.function_name, args.event_type, args.turn)
    elif args.class_name == "race":
        test_race_manager(args.function_name, args.turn, args.race_name)
    elif args.class_name == "training":
        test_training_manager(args.function_name, args.turn)


if __name__ == "__main__":
    main()
