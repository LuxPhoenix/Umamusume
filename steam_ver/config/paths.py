"""
Centralized path configuration for Steam version.

This module provides consistent path resolution across the entire Steam version.
All file paths should be accessed through this module to ensure consistency
and make it easy to reorganize the project structure.

Usage:
    from config.paths import Paths

    # Load dictionary
    data = json.load(open(Paths.DICTIONARY_STEAM))

    # Get deck config
    deck_path = Paths.get_deck_config("Oguri_Cap")
"""

from pathlib import Path
from typing import Optional


class Paths:
    """Centralized path management for the Steam version."""

    # ==================== ROOT DIRECTORIES ====================

    # Steam version root (where this config file is located)
    STEAM_ROOT = Path(__file__).parent.parent

    # Project root (parent of steam_ver)
    PROJECT_ROOT = STEAM_ROOT.parent

    # ==================== DATA DIRECTORIES ====================

    # Main data directory (shared between versions)
    DATA_DIR = PROJECT_ROOT / "data"

    # Version-specific data
    VERSION_DIR = DATA_DIR / "version"

    # JSON configurations
    JSON_DIR = DATA_DIR / "json"

    # Support card data
    SUPPORT_CARD_DATA_DIR = DATA_DIR / "support_card_data"

    # Manual setup events
    MANUAL_SETUP_EVENT_DIR = DATA_DIR / "manual_setup_event"

    # Support card events
    SPCARD_EVENT_DIR = DATA_DIR / "spcard_event"

    # ==================== ASSETS DIRECTORIES ====================

    # Main assets directory
    ASSETS_DIR = PROJECT_ROOT / "assets"

    # General training assets
    GENERAL_TRAINING_DIR = ASSETS_DIR / "generaltraining"

    # Mood assets
    MOOD_DIR = ASSETS_DIR / "mood"

    # Race assets
    RACES_DIR = ASSETS_DIR / "races"

    # Skill assets
    SKILL_DIR = ASSETS_DIR / "skill"

    # Strategy assets
    STRATEGY_DIR = ASSETS_DIR / "strategy"

    # Training scenario card assets
    TSCARD_DIR = ASSETS_DIR / "tscard"

    # ==================== STEAM-SPECIFIC DIRECTORIES ====================

    # Core modules
    CORE_DIR = STEAM_ROOT / "core"

    # Event handlers
    EVENTS_DIR = STEAM_ROOT / "events"

    # Game utilities
    GAME_UTILS_DIR = STEAM_ROOT / "game_utils"

    # UI modules
    UI_DIR = STEAM_ROOT / "ui"

    # General utilities
    UTILS_DIR = STEAM_ROOT / "utils"

    # Log files
    LOGS_DIR = STEAM_ROOT / "logs"

    # Test files
    TEST_DIR = STEAM_ROOT / "test"

    # Configuration
    CONFIG_DIR = STEAM_ROOT / "config"

    # Services
    SERVICES_DIR = STEAM_ROOT / "services"

    # ==================== SPECIFIC FILES ====================

    # Main dictionary configuration
    DICTIONARY_STEAM = VERSION_DIR / "dictionary_steam.json"

    # Default deck configuration
    DEFAULT_DECK = MANUAL_SETUP_EVENT_DIR / "default.json"

    # Horse information
    HORSE_INFO = STEAM_ROOT / "horse_info.json"

    # Support card information
    SUPPORT_CARD_INFO = STEAM_ROOT / "support_card.json"

    # Manual events
    MANUAL_JSON = STEAM_ROOT / "manual.json"

    # Event information
    EVENT_INFO = STEAM_ROOT / "event_info.json"

    # ==================== HELPER METHODS ====================

    @staticmethod
    def get_deck_config(deck_name: str) -> Path:
        """
        Get path to a specific deck configuration file.

        Args:
            deck_name: Name of the deck.

        Returns:
            Path to the deck configuration JSON file.

        Example:
            >>> Paths.get_deck_config("Oguri_Cap")
            Path('e:/AI Project/Umamusume/data/json/Oguri_Cap.json')
        """
        return Paths.MANUAL_SETUP_EVENT_DIR / f"{deck_name}.json"

    @staticmethod
    def get_support_card_event(card_name: str) -> Path:
        """
        Get path to a specific support card data file.

        Args:
            card_name: Name of the support card.

        Returns:
            Path to the support card data JSON file.
        """
        return Paths.SPCARD_EVENT_DIR / f"{card_name}.json"

    @staticmethod
    def get_asset(category: str, filename: str) -> Path:
        """
        Get path to a specific asset file.

        Args:
            category: Asset category (e.g., 'generaltraining', 'mood', 'races').
            filename: Asset filename (with or without extension).

        Returns:
            Path to the asset file.

        Example:
            >>> Paths.get_asset("generaltraining", "Training.png")
            Path('e:/AI Project/Umamusume/assets/generaltraining/Training.png')
        """
        return Paths.ASSETS_DIR / category / filename

    @staticmethod
    def get_log_file(filename: str) -> Path:
        """
        Get path to a log file.

        Args:
            filename: Log filename.

        Returns:
            Path to the log file.
        """
        Paths.ensure_dir_exists(Paths.LOGS_DIR)
        return Paths.LOGS_DIR / filename

    @staticmethod
    def ensure_dir_exists(dir_path: Path) -> None:
        """
        Ensure a directory exists, create it if it doesn't.

        Args:
            dir_path: Path to the directory.
        """
        dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def is_valid() -> bool:
        """
        Check if all critical paths exist.

        Returns:
            True if all critical paths exist, False otherwise.
        """
        critical_paths = [
            Paths.PROJECT_ROOT,
            Paths.DATA_DIR,
            Paths.ASSETS_DIR,
            Paths.STEAM_ROOT,
        ]

        return all(path.exists() for path in critical_paths)

    @classmethod
    def validate(cls) -> None:
        """
        Validate that all critical paths exist.

        Raises:
            FileNotFoundError: If any critical path is missing.
        """
        if not cls.is_valid():
            missing = [
                str(path)
                for path in [
                    cls.PROJECT_ROOT,
                    cls.DATA_DIR,
                    cls.ASSETS_DIR,
                    cls.STEAM_ROOT,
                ]
                if not path.exists()
            ]
            raise FileNotFoundError(f"Critical paths missing: {', '.join(missing)}")
