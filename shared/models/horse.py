"""
Horse Girl base model.

This module provides the base HorseGirl class 
"""

from typing import Tuple, Dict, List, Optional, Any
from .support_card import SupportCard


class HorseGirl:
    """
    Base class for Umamusume horse girl characters.

    Attributes:
        name: Character name.
        supportcard: Tuple of support cards used in training.
        friend_support: Friend support card name.
        training_priority: Base score list for training options.
        special_events: List of special events (script/character/card unique).
        skill_set: Tuple of skills to learn.
        strategy: Race strategy by distance.
    """

    def __init__(
        self,
        name: str,
        supportcard: Optional[Tuple[SupportCard, ...]] = None,
        friend_support: Optional[str] = None,
        race_table: Optional[Dict[int, str]] = None,
        training_priority: Optional[List[int]] = None,
        special_events: Optional[List[str]] = None,
        skill_set: Optional[Tuple[str, ...]] = None,
        strategy: Optional[Dict[int, str]] = None,
        default_info: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a horse girl character.

        Args:
            name: Character name.
            supportcard: Support card tuple.
            friend_support: Friend support card name.
            race_table: Race schedule by turn.
            training_priority: Training priority scores.
            special_events: Special event names.
            skill_set: Skills to learn.
            strategy: Race strategy configuration.
            default_info: Default information from JSON.
        """
        self.name = name
        self.supportcard = supportcard
        self.friend_support = friend_support
        self.race_table = race_table
        self.training_priority = training_priority
        self.special_events = special_events
        self.skill_set = skill_set
        self.strategy = strategy
        self._default_info = default_info or {}