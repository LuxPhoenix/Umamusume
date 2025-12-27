"""
Horse service for managing horse girl characters and support cards.

This service provides a clean interface for creating and managing
horse girl characters with their configurations.
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.models import HorseGirl, SupportCard
from .config_service import ConfigService


class HorseService:
    """
    Service for managing horse girl characters.

    This service handles the creation and configuration of horse girl
    characters, including loading their data from JSON files.
    """

    _horse_cache: Dict[str, HorseGirl] = {}
    _support_card_cache: Dict[str, SupportCard] = {}

    @classmethod
    def create_horse_girl(
        cls,
        name: str,
        supportcard: Optional[Tuple[str, ...]] = None,
        friend_support: Optional[str] = None,
        **kwargs,
    ) -> HorseGirl:
        """
        Create a horse girl character with configuration from JSON.

        Args:
            name: Character name.
            supportcard: Override support card names (optional).
            friend_support: Override friend support card (optional).
            **kwargs: Additional overrides for character attributes.

        Returns:
            Configured HorseGirl instance.
        """
        # Check cache first
        cache_key = f"{name}_{supportcard}_{friend_support}"
        if cache_key in cls._horse_cache:
            return cls._horse_cache[cache_key]

        # Load horse info from JSON
        horse_data = ConfigService.load_horse_info()

        if name not in horse_data:
            raise ValueError(f"Horse girl '{name}' not found in horse_info.json")

        default_info = horse_data[name]

        # Get support cards
        sc_names = supportcard or default_info.get("default_supportcard", [])
        support_cards = tuple(cls.get_support_card(sc) for sc in sc_names)

        # Get friend support
        friend = friend_support or default_info.get("friend_supportcard")

        # Get other attributes
        training_priority = kwargs.get("training_priority") or default_info.get(
            "training_priority"
        )
        special_events = kwargs.get("special_events") or default_info.get(
            "special_events"
        )
        skill_set = kwargs.get("skill_set") or tuple(default_info.get("skill_set", []))

        # Convert strategy keys to int
        strategy = default_info.get("strategy", {})
        if strategy:
            strategy = {int(k): v for k, v in strategy.items()}

        # Create horse girl
        horse = HorseGirl(
            name=name,
            supportcard=support_cards,
            friend_support=friend,
            training_priority=training_priority,
            special_events=special_events,
            skill_set=skill_set,
            strategy=strategy,
            default_info=default_info,
        )

        # Cache it
        cls._horse_cache[cache_key] = horse

        return horse

    @classmethod
    def get_support_card(cls, card_name: str) -> SupportCard:
        """
        Get or create a support card.

        Args:
            card_name: Support card name.

        Returns:
            SupportCard instance.
        """
        # Check cache
        if card_name in cls._support_card_cache:
            return cls._support_card_cache[card_name]

        # Load support card info
        try:
            all_cards = ConfigService.load_support_card_info()
            card_data = all_cards.get(card_name, {})
        except Exception:
            card_data = {}

        # Create support card
        card = SupportCard(
            name=card_name,
            card_type=card_data.get("type"),
            rarity=card_data.get("rarity"),
            level=card_data.get("level", 1),
            limit_break=card_data.get("limit_break", 0),
            data=card_data,
        )

        # Cache it
        cls._support_card_cache[card_name] = card

        return card

    @classmethod
    def list_available_horses(cls) -> list[str]:
        """
        List all available horse girl names.

        Returns:
            List of horse girl names.
        """
        horse_data = ConfigService.load_horse_info()
        return list(horse_data.keys())

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the horse and support card cache."""
        cls._horse_cache.clear()
        cls._support_card_cache.clear()
