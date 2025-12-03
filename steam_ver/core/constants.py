"""
Game constants and configuration values.

This module contains all magic numbers, thresholds, and configuration
constants used throughout the game automation.
"""


class GameWindow:
    """Game window configuration constants."""
    TITLE = "Umamusume"
    TARGET_WIDTH = 1440


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
