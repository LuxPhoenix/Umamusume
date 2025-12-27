"""
Asset service for managing game assets (images, icons, etc.).

This service provides methods for accessing game assets
without hardcoding paths throughout the codebase.
"""

from pathlib import Path
from typing import Optional

from config.paths import Paths


class AssetService:
    """
    Service for managing game assets.

    This service provides a clean interface for accessing various game assets
    like training icons, mood indicators, race images, etc.
    """

    # Asset categories
    GENERAL_TRAINING = "generaltraining"
    MOOD = "mood"
    RACES = "races"
    SKILL = "skill"
    STRATEGY = "strategy"
    TSCARD = "tscard"

    @staticmethod
    def get_asset_path(category: str, filename: str) -> Path:
        """
        Get the full path to an asset file.

        Args:
            category: Asset category (e.g., 'generaltraining', 'mood').
            filename: Asset filename (automatically adds .png if no extension).

        Returns:
            Path to the asset file.

        Example:
            >>> path = AssetService.get_asset_path("mood", "Good")
            >>> # Returns: Path('assets/mood/Good.png')
        """
        # Add .png extension if not present
        if not filename.endswith((".png", ".jpg", ".jpeg")):
            filename = f"{filename}.png"

        return Paths.get_asset(category, filename)

    @staticmethod
    def get_training_asset(filename: str) -> Path:
        """
        Get path to a general training asset.

        Args:
            filename: Asset filename.

        Returns:
            Path to the training asset.
        """
        return AssetService.get_asset_path(AssetService.GENERAL_TRAINING, filename)

    @staticmethod
    def get_mood_asset(mood: str) -> Path:
        """
        Get path to a mood indicator asset.

        Args:
            mood: Mood name (e.g., 'Good', 'Bad', 'Normal', 'Awful').

        Returns:
            Path to the mood asset.
        """
        return AssetService.get_asset_path(AssetService.MOOD, mood)

    @staticmethod
    def get_race_asset(race_name: str) -> Path:
        """
        Get path to a race asset.

        Args:
            race_name: Race name.

        Returns:
            Path to the race asset.
        """
        return AssetService.get_asset_path(AssetService.RACES, race_name)

    @staticmethod
    def get_skill_asset(skill_name: str) -> Path:
        """
        Get path to a skill asset.

        Args:
            skill_name: Skill name.

        Returns:
            Path to the skill asset.
        """
        return AssetService.get_asset_path(AssetService.SKILL, skill_name)

    @staticmethod
    def get_strategy_asset(strategy_name: str) -> Path:
        """
        Get path to a strategy asset.

        Args:
            strategy_name: Strategy name.

        Returns:
            Path to the strategy asset.
        """
        return AssetService.get_asset_path(AssetService.STRATEGY, strategy_name)

    @staticmethod
    def asset_exists(category: str, filename: str) -> bool:
        """
        Check if an asset file exists.

        Args:
            category: Asset category.
            filename: Asset filename.

        Returns:
            True if asset exists, False otherwise.
        """
        return AssetService.get_asset_path(category, filename).exists()

    @staticmethod
    def list_assets(category: str, pattern: str = "*.png") -> list[Path]:
        """
        List all assets in a category.

        Args:
            category: Asset category.
            pattern: File pattern (default: "*.png").

        Returns:
            List of asset paths.
        """
        category_path = Paths.ASSETS_DIR / category
        if not category_path.exists():
            return []

        return list(category_path.glob(pattern))
