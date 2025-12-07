"""
Generic JSON file loader with error handling.

This utility provides a centralized way to load JSON files
with proper error handling and logging.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import traceback
from shared.utils.logger import Logger

logger = Logger.get_logger("JSONLoader")

class JSONLoader:
    """Generic JSON file loader with error handling."""

    @staticmethod
    def load(file_path: Path) -> Dict[str, Any]:
        """
        Load a JSON file.

        Args:
            file_path: Path to the JSON file.

        Returns:
            Parsed JSON data as dictionary.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file contains invalid JSON.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logger.error(traceback.format_exc())
            raise json.JSONDecodeError(
                f"Invalid JSON in {file_path}: {e.msg}", e.doc, e.pos
            )

    @staticmethod
    def load_safe(
        file_path: Path, default: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load a JSON file with fallback to default value.

        Args:
            file_path: Path to the JSON file.
            default: Default value if file doesn't exist or is invalid.

        Returns:
            Parsed JSON data or default value.
        """
        try:
            return JSONLoader.load(file_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return default or {}

    @staticmethod
    def save(file_path: Path, data: Dict[str, Any], indent: int = 4) -> None:
        """
        Save data to a JSON file.

        Args:
            file_path: Path to save the JSON file.
            data: Data to save.
            indent: JSON indentation level.
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
