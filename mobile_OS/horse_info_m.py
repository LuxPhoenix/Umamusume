"""Store data from horse_info.json into class objects HorseGirl, making it convenient to use."""
import json
from support_card_m import SupportCard

class HorseGirl:
    """Implement umamusume object with following attributes:
    
    self.supportcard: a tuple of six support cards by default used in training.

    self.friend_supportcard: a string, the support card to be borrowed from friends.

    self.racetable: a dictionary consisting of races to be attended as values and their
    corresponding turn number as key. 

    self.training_priority: the base score list for different training options. Normally, we want
    to prioritize speed training, then stamina & power, then wit, then guts for the least prioritized training.
    
    self.special_events: a list of special events that is script-unique, character unique, or support card unique.
    
    self.DI: a dictionary of the default information for this horse girl."""

    def __init__(self, name: str, supportcard: tuple = None, 
                 friend_support: str = None, race_table: dict = None, 
                 training_priority: list = None, special_events: list = None,
                 skill_set: tuple = None):
        try:
            with open('horse_info_m.json', 'r') as file:
                self.DI = json.load(file)[name]
        except FileNotFoundError:
            print("Error: The file 'horse_info_m.json' was not found.")
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from the file. Check for valid JSON format.")
        self.name = self.DI["name"]
        sc = supportcard if supportcard else self.DI['default_supportcard']
        self.supportcard = tuple(SupportCard(i) for i in sc)
        self.friend_support = friend_support if friend_support else self.DI['friend_supportcard']
        d = race_table if race_table else self.DI['default_racetable'] 
        self.race_table = {int(k): v for k, v in d.items()}  # Make sure keys are integers rather than string.
        self.training_priority = training_priority if training_priority else self.DI['training_priority']  # Deprecated.
        self.special_events = special_events if special_events else self.DI['special_events']

        """The available skill set will include:
        1. The initial skills of the Umamusume.
        2. Skills obtainable from hints of the selected support cards.
        3. Skills obtainable from events of the support cards.
        4. Skills obtainable from races attended by the Umamusume. (Currently not implemented)"""
        sc_h = [supcard.skill_h for supcard in self.supportcard]
        sc_e = [supcard.event_skill for supcard in self.supportcard]
        self.available_skills = set().union(self.DI["initial_skill"], *sc_h, *sc_e)
        self.skill_set = skill_set if skill_set else tuple(self.DI['skill_set'])

        self.strategy = {int(k): v for k, v in self.DI["strategy"].items()}

    def load(self, purpose: str = "fan farming", scenerio: str = "URA"):
        """Load different scenerios with different purposes."""
        if "CM" in scenerio:
            self._load_CM(scenerio)
        if purpose in ["parent farming", "debuffer training", "team trial"]:
            return {"hint_priority": 4.5}
        else:
            return {"hint_priority": 0.5}

    def _load_CM(self, name: str):
        """For CM parents
        Useful skills from each supportcard w.r.t the CM will be marked.
        Priority to pickup hints will increase.
        Event choice will focus on relavent skills (Not implemented yet).
        
        name: the name of the CM cup, will be passed by scenerio."""
        try:
            with open('skill_set.json', 'r') as file:
                CM_skills = json.load(file)[name][self.strategy[1]]
        except FileNotFoundError:
            print("Error: The file 'skill_set.json' was not found.")
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from the file. Check for valid JSON format.")
        for key in CM_skills.keys():
            for supcard in self.supportcard:
                for skill in set().union(supcard.skill_h, supcard.event_skill):
                    if skill in CM_skills[key]:
                        skill.priority = float(key)
            

        



'''
Oguri_Cap = HorseGirl("Oguri Cap")
Oguri_Cap3 = HorseGirl("Oguri Cap3")
Daiwa_Scarlet = HorseGirl("Daiwa Scarlet")
Maruzensky = HorseGirl("Maruzensky")
El_Condor = HorseGirl("El Condor")
Maruzensky2 = HorseGirl("Maruzensky2")
'''
Tokai_Teio2 = HorseGirl("Tokai Teio2")
TM_Opera_O = HorseGirl("T.M. Opera O")
Maruzensky3 = HorseGirl("Maruzensky3")
El_Condor1 = HorseGirl("El Condor1")
Vodca = HorseGirl("Vodca")

if __name__ == "__main__":
    Vodca.load(scenerio="CMCancerCup")
    print(Vodca.available_skills)
