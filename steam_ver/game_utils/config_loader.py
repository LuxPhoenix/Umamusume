"""
Configuration file loading utilities.

DEPRECATED: This module is kept for backward compatibility.
New code should use services.ConfigService instead.

This module handles loading JSON configuration files.
"""

from typing import Dict, Any
from services import ConfigService


class ConfigLoader:
    """
    Handles configuration file loading.

    DEPRECATED: Use services.ConfigService instead.
    This class now wraps ConfigService for backward compatibility.
    """

    @staticmethod
    def load_dictionary() -> Dict[str, Any]:
        """
        Load the main dictionary configuration.

        Returns:
            Dictionary configuration.

        Deprecated:
            Use ConfigService.load_dictionary() instead.
        """
        return ConfigService.load_dictionary()

    @staticmethod
    def load_deck_config(deck_name: str) -> Dict[str, Any]:
        """
        Load deck-specific configuration.

        Args:
            deck_name: Name of the deck.

        Returns:
            Deck configuration or None if not found.

        Deprecated:
            Use ConfigService.load_deck_config() instead.
        """
        return ConfigService.load_deck_config(deck_name, use_default_on_error=True)

    @staticmethod
    def load_support_card_event(card_name: str) -> Dict[str, Any]:
        """
        Load support card data.

        Args:
            card_name: Name of the support card.

        Returns:
            Support card data dictionary.

        Deprecated:
            Use ConfigService.load_support_card_data() instead.
        """
        return ConfigService.load_support_card_event(card_name)
