"""Store data from horse_info.json into class objects HorseGirl, making it convenient to use."""
import json


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
                 training_priority: list = None, special_events: list = None):
        self.name = name
        try:
            with open('horse_info.json', 'r') as file:
                self.DI = json.load(file)[self.name]
        except FileNotFoundError:
            print("Error: The file 'horse_info.json' was not found.")
        except json.JSONDecodeError:
            print("Error: Could not decode JSON from the file. Check for valid JSON format.")
        self.supportcard = supportcard if supportcard else self.DI['default_supportcard']
        self.friend_support = friend_support if friend_support else self.DI['friend_supportcard']
        d = race_table if race_table else self.DI['default_racetable'] 
        self.race_table = {int(k): v for k, v in d.items()}  # Make sure keys are integers rather than string.
        self.training_priority = training_priority if training_priority else self.DI['training_priority']
        self.special_events = special_events if special_events else self.DI['special_events']


Oguri_Cup = HorseGirl("Oguri Cup")
Daiwa_Scarlet = HorseGirl("Daiwa Scarlet")
Maruzensky = HorseGirl("Maruzensky")

if __name__ == "__main__":
    print(Oguri_Cup.race_table, Oguri_Cup.supportcard)
