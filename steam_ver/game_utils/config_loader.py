"""
Configuration file loading utilities.

This module handles loading JSON configuration files.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from utils.logger import Logger

logger = Logger.get_logger()


class ConfigLoader:
    """Handles configuration file loading."""

    @staticmethod
    def load_dictionary() -> Dict[str, Any]:
        """
        Load the main dictionary configuration.

        Returns:
            Dictionary configuration.
        """
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
