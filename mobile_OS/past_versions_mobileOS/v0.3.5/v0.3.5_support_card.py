"""Implements support cards as a class object. Information about support cards in game are inherited from support_card.json"""
import json


class SupportCard():
    """Return a support card object with following attributes:
    
    1. self.name
    2. self.train_type: the specialized training type for the support card.
    3. self.friendship: a bool value that is 1 if friendship bar turns orange or maxed, and 0 otherwise.
    4. self.e_train: train effectiveness
    5. self.e_mood: mood bonus
    6. self.e_friend: friendship bonus"""

    def __init__(self, name):
        """train_type is any elements from (spe, sta, pow, gut, wit)"""
        self.name = name
        try:
            with open('support_card.json', 'r') as file:
                content = json.load(file)[self.name]
        except FileNotFoundError:
            print("Error: The file 'support_card.json' was not found.")
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from the file. Check for valid JSON format.")
        self.train_type = content["train_type"]
        self.e_train = float(content["training_effectiveness"])
        self.e_mood = float(content["mood_bunus"])
        self.e_friend = float(content["friend_bonus"])
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
