"""
Data models and enumerations.

This module contains dataclasses, enums, and custom exceptions
used throughout the game automation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


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


class MoodLevel(Enum):
    """Mood level enumeration."""
    AWFUL = "Awful"
    BAD = "Bad"
    NORMAL = "Normal"
    GOOD = "Good"
    GREAT = "Great"


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

    def offset(self, dx: float = 0, dy: float = 0) -> 'Coordinate':
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
