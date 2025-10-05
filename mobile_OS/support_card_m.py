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

    def __init__(self, name: str, LBlevel: int = 4):
        """train_type is any elements from (spe, sta, pow, gut, wit)"""
        self.name = name
        try:
            with open('support_card_m.json', 'r') as file:
                content = json.load(file)[self.name]
        except FileNotFoundError:
            print("Error: The file 'support_card.json' was not found.")
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from the file. Check for valid JSON format.")
        self.train_type = content["train_type"]
        self.e_train = float(content["training_effectiveness"][LBlevel])
        self.e_mood = float(content["mood_bonus"][LBlevel])
        self.e_friend = float(content["friend_bonus"][LBlevel])
        self.friendship = 0
        self.hint_priority = float(content["hint_priority"])
        self.skill_h = [Skill(i) for i in content["skill_hint"]]
        self.event_skill = [Skill(i) for i in content["event_skill"]]
        self.h_level = content["hint_levels"][LBlevel]  # It's not the "h" you are thinking about!
        self.h_frequency = content["hint_frequency"][LBlevel]

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

    @property
    def h_score(self):
        """The average priority of the skills from hints will represent the h_score."""
        return sum(skill.priority for skill in self.skill_h) / max(len(self.skill_h), 1)


class Skill:
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Skill({self.name}, {self.priority})"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Skill):
            return (self.name == other.name and self.priority == other.priority)

    def __hash__(self):
        return 0


if __name__ == "__main__":
    KitasanBlackSpe = SupportCard("Kitasan Black SSR spe", 4)
    print(KitasanBlackSpe.e_mood)
    print(KitasanBlackSpe.h_level, KitasanBlackSpe.skill_h)
    print("I love Umamusume" == Skill("I love Umamusume"))
    print("A" in [Skill("A"), Skill("B")])
    print(Skill("A") in ("A", "B"))
    print(KitasanBlackSpe.h_score)

        