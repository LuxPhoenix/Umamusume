"""
Event matching utilities.

This module handles matching detected events to known events using text similarity.
"""

from typing import Dict, Any, Optional

import jiwer

from core.constants import EventMatching


class EventMatcher:
    """Handles event matching using text similarity."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for comparison.

        Args:
            text: Text to normalize.

        Returns:
            Normalized text.
        """
        return jiwer.RemovePunctuation()(text.lower())

    @staticmethod
    def match_event(
        detected_name: str,
        event_list: Dict[str, Any]
    ) -> Optional[str]:
        """
        Match detected event name to known events using WER.

        Args:
            detected_name: Detected event name.
            event_list: Dictionary of known events.

        Returns:
            Matched event name or None if no good match found.
        """
        if not event_list:
            return None

        best_match = None
        best_score = float('inf')
        
        norm_detected = EventMatcher.normalize_text(detected_name)

        for key in event_list.keys():
            norm_key = EventMatcher.normalize_text(key)
            score = jiwer.wer(norm_detected, norm_key)
            
            if score < best_score:
                best_score = score
                best_match = key

        if best_score < EventMatching.WER_THRESHOLD:
            return best_match
        return None
