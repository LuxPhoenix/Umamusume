"""
Training management logic.

This module handles training selection, support card friendship,
and training execution.
"""

import time
from typing import List, Dict, Any, Tuple

import pyautogui
from pyautogui import ImageNotFoundException

from core.constants import (
    ImagePath, TrainingScore, FriendshipColor, WaitTime, ImageConfidence
)
from core.models import TrainingType, ContinueException
from ui.image_recognition import ImageRecognition
from utils.logger import Logger
from horse_info import SupportCard

logger = Logger.get_logger()


class TrainingManager:
    """Manages training operations."""

    @staticmethod
    def update_support_card_friendship(
        support_card: SupportCard,
        region: Tuple[int, int, int, int],
        confidence: float = ImageConfidence.VERY_HIGH
    ) -> None:
        """
        Check and update support card friendship status.

        Args:
            support_card: Support card to check.
            region: Screen region where card is located.
            confidence: Confidence threshold for image matching.
        """
        if support_card.friendship:
            return  # Already maxed

        # Check pixel color for orange bar
        r, g, b = pyautogui.pixel(
            int(region[0] + 10),
            int(region[1] + 50)
        )
        
        color_distance = (
            (r - FriendshipColor.ORANGE_R) ** 2 +
            (g - FriendshipColor.ORANGE_G) ** 2 +
            (b - FriendshipColor.ORANGE_B) ** 2
        )

        if color_distance < FriendshipColor.COLOR_THRESHOLD:
            support_card.friendship = 1
            logger.debug(f"Orange bar detected for {support_card}")
            return

        # Check for max friendship icon
        try:
            pyautogui.locateOnScreen(
                f"{ImagePath.BASE_DIR}/{ImagePath.GENERAL_TRAINING}/"
                f"friendship_max.png",
                region=(region[0] - 30, region[1] + 25, 60, 35),
                confidence=confidence
            )
            support_card.friendship = 1
            logger.debug(f"Max friendship detected for {support_card}")
        except ImageNotFoundException:
            logger.debug(
                f"Friendship not maxed for {support_card}: "
                f"{support_card.friendship}"
            )

    @staticmethod
    def calculate_friendship_bonus(
        training_type: str,
        support_cards: List[SupportCard],
        turn: int
    ) -> float:
        """
        Calculate friendship bonus for training.

        Args:
            training_type: Type of training.
            support_cards: List of support cards to check.
            turn: Current turn number.

        Returns:
            Total bonus score.
        """
        cards_to_check = support_cards.copy()
        total_score = 0.0
        participating_cards = []

        for card in cards_to_check:
            coord = ImageRecognition.test_image(
                f"tscard/{card.name}",
                return_coordinate=True
            )
            
            if coord:
                TrainingManager.update_support_card_friendship(card, region=coord)
                support_cards.remove(card)
                total_score += card.score(training_type, 1)
                participating_cards.append(card.name)

        if participating_cards:
            logger.info(
                f"Turn {turn}: Training {training_type} with "
                f"{participating_cards}, bonus: {total_score}"
            )

        return total_score

    @staticmethod
    def select_best_training(
        turn: int,
        mood_score: float,
        character,
        click_func,
        click_multiple_func,
        raise_mood_func,
        check_date_event_func,
        check_extra_training_func,
        cfg: Dict[str, Any]
    ) -> None:
        """
        Select and execute best training option.

        Args:
            turn: Current turn number.
            mood_score: Current mood score.
            character: Character with training priorities and support cards.
            click_func: Function to perform clicks.
            click_multiple_func: Function to perform multiple clicks.
            raise_mood_func: Function to raise mood.
            check_date_event_func: Function to check for date events.
            check_extra_training_func: Function to check extra training.
            cfg: Game configuration.

        Raises:
            ContinueException: After training or mood raising.
        """
        logger.debug(f"Turn {turn}: Evaluating training options")

        training_types = [
            TrainingType.SPEED.value,
            TrainingType.STAMINA.value,
            TrainingType.POWER.value,
            TrainingType.GUTS.value,
            TrainingType.WITS.value
        ]
        
        unpresented_cards = list(character.supportcard)

        try:
            click_func(cfg["root"]["daily_training"]["training"], 2)
            
            # Initialize scores with character priorities plus mood
            scores = character.training_priority + [mood_score]
            
            # Avoid clicking same option as previous turn
            pre_trainoption = getattr(character, 'pre_trainoption', 0)
            check_order = [
                (pre_trainoption + i) % 5
                for i in range(1, 6)
            ]

            # Evaluate each training option
            for idx in check_order:
                training_coord = [
                    cfg["training_option"]["speed"][0] + 80 * idx,
                    cfg["training_option"]["speed"][1]
                ]
                click_func(training_coord, 0)

                # Add friendship bonus
                scores[idx] += TrainingManager.calculate_friendship_bonus(
                    training_types[idx],
                    unpresented_cards,
                    turn
                )

                # Add NPC bonuses
                if ImageRecognition.test_image(f"{ImagePath.URA}/Director"):
                    scores[idx] += TrainingScore.DIRECTOR_BONUS
                if ImageRecognition.test_image(f"{ImagePath.URA}/Reporter"):
                    scores[idx] += TrainingScore.REPORTER_BONUS

                logger.debug(f"Training option {idx + 1} score: {scores[idx]}")

            # Select best option
            max_index = scores.index(max(scores))

            if max_index == 5:
                # Best option is to raise mood instead
                click_func(cfg["root"]["back_button"], 1)
                raise_mood_func()
                check_date_event_func()
                raise ContinueException
            else:
                # Execute training
                training_coord = [
                    cfg["training_option"]["speed"][0] + max_index * 80,
                    cfg["training_option"]["speed"][1]
                ]
                wait_time = cfg["wait_time"]["_check_training_"]
                click_multiple_func(training_coord, 4, wait_time)
                
                # Update pre_trainoption
                character.pre_trainoption = max_index
                
                logger.info(
                    f"Turn {turn}: Selected {training_types[max_index]} "
                    f"training, score: {scores[max_index]}"
                )
                
                check_extra_training_func()
                raise ContinueException

        except ImageNotFoundException as e:
            logger.error(f"Training selection failed: {e}")
