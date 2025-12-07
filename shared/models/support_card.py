"""
Support Card base model.

This module provides the base SupportCard class
"""

from typing import Dict, Any, Optional


class SupportCard:
    """
    Represents a support card in Umamusume.

    Attributes:
        name: Name of the support card.
        type: Type of the card (Speed, Stamina, Power, Guts, Wisdom, Friend).
        rarity: Rarity level (SSR, SR, R).
        level: Card level.
        limit_break: Limit break level (0-4).
    """

    def __init__(
        self,
        name: str,
        card_type: Optional[str] = None,
        rarity: Optional[str] = None,
        level: Optional[int] = None,
        limit_break: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a support card.

        Args:
            name: Card name.
            card_type: Card type (Speed, Stamina, etc.).
            rarity: Card rarity.
            level: Card level.
            limit_break: Limit break level.
            data: Additional card data from JSON.
        """
        self.name = name
        self.type = card_type
        self.rarity = rarity
        self.level = level or 1
        self.limit_break = limit_break or 0
        self.data = data or {}
