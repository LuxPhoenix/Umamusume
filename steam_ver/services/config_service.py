"""
Configuration service for loading and managing game configurations.

This service provides a clean interface for loading various configuration files
without exposing the underlying file system structure.
"""

from typing import Dict, Any, Optional
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config import JSONLoader
from config.paths import Paths
from shared.utils.logger import Logger

logger = Logger.get_logger()


class ConfigService:
    """
    Service for loading and managing configuration files.

    This service abstracts away the details of where configuration files
    are stored and provides a simple interface for loading them.
    """

    @staticmethod
    def load_dictionary() -> Dict[str, Any]:
        """
        Load the main game dictionary configuration.

        Returns:
            Dictionary configuration data.
        """
        return JSONLoader.load(Paths.DICTIONARY_STEAM)

    @staticmethod
    def load_deck_config(
        deck_name: str, use_default_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Load a specific deck configuration.

        Args:
            deck_name: Name of the deck to load.
            use_default_on_error: If True, load default deck on error.

        Returns:
            Deck configuration data.
        """
        deck_path = Paths.get_deck_config(deck_name)

        if use_default_on_error:
            try:
                return JSONLoader.load(deck_path)
            except (FileNotFoundError, Exception):
                # Fallback to default deck
                logger.info(f"Deck '{deck_name}' not found. Loading default deck.")
                return JSONLoader.load(Paths.DEFAULT_DECK)
        else:
            return JSONLoader.load(deck_path)

    @staticmethod
    def save_deck_config(deck_name: str, config_data: Dict[str, Any]) -> None:
        """
        Save a deck configuration.

        Args:
            deck_name: Name of the deck.
            config_data: Configuration data to save.
        """
        deck_path = Paths.get_deck_config(deck_name)
        JSONLoader.save(deck_path, config_data)

    @staticmethod
    def load_horse_info() -> Dict[str, Any]:
        """
        Load horse girl information.

        Returns:
            Horse girl information data.
        """
        return JSONLoader.load(Paths.HORSE_INFO)

    @staticmethod
    def load_support_card_info() -> Dict[str, Any]:
        """
        Load support card information.

        Returns:
            Support card information data.
        """
        return JSONLoader.load(Paths.SUPPORT_CARD_INFO)

    @staticmethod
    def load_support_card_event(card_name: str) -> Dict[str, Any]:
        """
        Load detailed data for a specific support card.

        Args:
            card_name: Name of the support card.

        Returns:
            Support card detailed data.
        """
        card_path = Paths.get_support_card_event(card_name)
        return JSONLoader.load(card_path)

    @staticmethod
    def load_manual_events() -> Dict[str, Any]:
        """
        Load manual event configuration.

        Returns:
            Manual event data.
        """
        return JSONLoader.load(Paths.MANUAL_JSON)

    @staticmethod
    def load_event_info() -> Dict[str, Any]:
        """
        Load event information.

        Returns:
            Event information data.
        """
        return JSONLoader.load(Paths.EVENT_INFO)

    @staticmethod
    def list_available_decks() -> list[str]:
        """
        List all available deck configurations.

        Returns:
            List of deck names (without .json extension).
        """
        if not Paths.MANUAL_SETUP_EVENT_DIR.exists():
            return []

        return [
            f.stem
            for f in Paths.MANUAL_SETUP_EVENT_DIR.glob("*.json")
            if f.name != "default.json"
        ]

    @staticmethod
    def deck_exists(deck_name: str) -> bool:
        """
        Check if a deck configuration exists.

        Args:
            deck_name: Name of the deck.

        Returns:
            True if deck exists, False otherwise.
        """
        return Paths.get_deck_config(deck_name).exists()
