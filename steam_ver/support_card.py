"""
Support card implementation.

REFACTORED: Now uses SupportCard from shared.models and ConfigService.
This module maintains backward compatibility with the original interface.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.models import SupportCard as BaseSupportCard
from services import ConfigService


class SupportCard(BaseSupportCard):
    """
    Support card with game-specific attributes.

    Attributes:
        name: Card name.
        train_type: Specialized training type.
        friendship: 1 if friendship bar is orange/maxed, 0 otherwise.
        e_train: Training effectiveness.
        e_mood: Mood bonus.
        e_friend: Friendship bonus.
    """

    def __init__(self, name: str):
        """
        Initialize support card from support_card.json.

        Args:
            name: Support card name.
        """
        # Load card data
        try:
            all_cards = ConfigService.load_support_card_info()
            content = all_cards.get(name, {})
        except Exception as e:
            print(f"Error loading support card data: {e}")
            content = {}

        # Initialize base class
        super().__init__(name=name, card_type=content.get("train_type"), data=content)

        # Game-specific attributes
        self.train_type = content.get("train_type", "")
        self.e_train = float(content.get("training_effectiveness", 0))
        self.e_mood = float(content.get("mood_bunus", 0))  # Note: typo in JSON
        self.e_friend = float(content.get("friend_bonus", 0))
        self.friendship = 0

    def _is_specialized(self, training_type: str):
        if self.train_type == training_type:
            return 1
        else:
            return 0

    def score(self, training_type: str, present: bool):
        """Return the training bonus score contributed by this support card to a specific training_type.

        If the card is not present under the training type, then score is 0.
        The score is 1 if this card is present and the relationship bar is not organge yet, since it is valuable to
        increase the relationship.
        The score is 2.4 if relationship bar is organge & maxed, and the support card is present under its specialized
        training type. This triggers friendship traininng, which is immensely valuable.
        The score is 0.6 if relationship is organge & maxed but rainbow training is not triggered. This mearly addes up the
        training effectiveness & mood bonus, so the benefit is smaller."""

        if not present:
            return 0
        if self.friendship:
            if self._is_specialized(training_type):
                return 2.4
            else:
                return 0.6
        else:
            return 1

    def __str__(self):
        return f"Support Card: {self.name}, current friendship: {self.friendship}"

    def __repr__(self):
        return f"SupportCard({self.name})"


if __name__ == "__main__":
    KitasanBlackSpe = SupportCard("Kitasan Black spe")
    print(type(KitasanBlackSpe.e_mood))
