import pyautogui
from pyautogui import ImageNotFoundException
import time
from builtins import Exception
import pygetwindow as gw
import json
from utils.logger import Logger
from utils.detect_text import ScreenTextReader
import math
import jiwer
from horse_info import *

logger = Logger.get_logger()

class UmaException(Exception):
    pass

class ContinueException(Exception):
    time.sleep(2)
    print("Continue to next turn.")
    pass

class UmaGame:
    """Everything integrated."""

    def __init__(self, support_card: tuple = None, race_day: list = None, manual_race_day: list = None, test: bool = 1, deck_name: str = "Cap"):
        """Adjust the coordinate system according to the device."""

        self.style = None
        self.pre_trainoption = None
        self.turn = 0
        self.race_day = race_day

        self.manual_race_day = manual_race_day  #manual race by user declair

        self.event_manage, self.cfg = self._settings_config(deck_name)

        self.list_event = self.setup_event(self.event_manage)
        self.x, self.y, self.w, self.h = self._settings_UI()  # Get the window position and size.

        self.screen_reader = ScreenTextReader()

    def setup_event(self, event_manage: dict):
        """Setup the event dictionary from the event_manage.

        Flattens the nested event_manage dictionary into a single-level
        dictionary of special events, excluding 'manual_race_day'.
        """
        special_events = {}
        for key, value in event_manage.items():
            if key != "manual_race_day":
                for sub_key, sub_value in value.items():
                    special_events[sub_key] = sub_value
        return special_events

    def _manual_setup(self, support_cards: list = None, deck_name: str = "manual"):
        dictionary = {}
        for card in support_cards:
            with open(f"data/SupportCardData/{card}.json", 'r', encoding='utf-8') as file:
                data = json.load(file)

            dictionary[card] = {}
            dct_card = dictionary[card]
            for key, value in data.items():
                if value["options"] == None or len(value["options"]) == 1: # No choice event
                    dct_card[key] = "Auto"
                else:
                    dct_card[key] = 0
        dictionary["manual_race_day"] = []
        
        with open(f"{deck_name}.json", 'w', encoding='utf-8') as file:
            json.dump(dictionary, file, ensure_ascii=False, indent=4)
        print("Manual setup completed. Data saved to dictionary.json.")
        return

    def _settings_UI(self):
        window_title = "Umamusume"
        window = gw.getWindowsWithTitle(window_title)[0]

        # Lấy kích thước hiện tại và tính tỉ lệ
        original_width, original_height = window.width, window.height
        aspect_ratio = original_width / original_height

        new_width = 1440
        new_height = int(new_width / aspect_ratio)

        # Áp dụng kích thước mới
        window.resizeTo(new_width, new_height)
        
        return (window.left, window.top, new_width, new_height)

    def _settings_config(self, deck_name):
        with open('data/json/dictionary.json', 'r', encoding='utf-8') as file:
            cfg = json.load(file)
            
        with open(f"{deck_name}.json", 'r', encoding='utf-8') as file:
            event_manage = json.load(file)
        
        return event_manage, cfg

    def _coordinate_for_click(self, a: float, b: float):
        """Adjust the true coordinate to the relative position on my macbook."""
        if self.test:
            a1 = self.xy[0] + (a - self.cfg["x0"])*self.xy[2]
            b1 = self.xy[1] + (b - self.cfg["y0"])*self.xy[3]
        else:
            a1, b1 = a, b  # If window on topright corner of my screen, do not conduct screen adjustment.
        return a1, b1
    
    def _click_game_ui(self, x, y, interval=0.5):
        """Click at the specified position in the game window."""
        return self.x + x, self.y + y
    
    def click(self, coord: tuple, interval=0.5):
        a1, b1 = self._click_game_ui(coord[0], coord[1])
        pyautogui.click(a1, b1)
        time.sleep(interval)
    
    def nclick(self, coord: tuple, n: int, interval=0.5):
        """Click by n times."""
        if n <= 1:
            self.click([coord[0], coord[1]], interval)
        else:
            a1, b1 = self._click_game_ui(coord[0], coord[1])
            for i in range(n):
                pyautogui.click(a1, b1)
                time.sleep(interval)
        
    def train_horse_loop(self, name: str, supportcard: tuple = None, style: str = "front", character: HorseGirl = Daiwa_Scarlet, turn = 1):
        """Train the horse with following logic.

        conduct this loop by day, starting from turn 0:

        day >= 72:
            Training URA -> Racing URA -> next day
        day = 30|54:
            Inspiration event -> Training UI
        day = 24|38:
            New Year event -> Training UI
        other:
            Choice event? -> Training UI

        training UI:
            if race_day:
                Race day UI -> Race UI -> Goal complete -> next day
            else: normal training UI
        
        normal training UI:
            if infirmary:
                Infirmary -> next day
            if race_scheduled:
                Race -> after_race event? -> next day
            if energy low:
                Recreation -> next day
            if mood bad:
                Raise mood -> date event? -> next day
            else:
                training -> extra_training event? -> next day
        """
        self.turn = turn
        self.style = style
        self.pre_trainoption = 0  # The default starting "previous" training is speed.
        self.cfg = character

        while self.turn <= 80:
            try:
                if self.turn >= 72:
                    self.URA_training()
                elif self.turn in [30, 54]:
                    self.inspiration_event()
                    self.train_horse(name, supportcard)
                elif self.turn in [24, 38]:
                    self.new_year_event()
                    self.train_horse(name, supportcard)
                else:
                    self._check_multiq()
                    self.train_horse(name, supportcard)
            except ContinueException:
                self.turn += 1
                time.sleep(6)
                continue

    def wait_choice_event(self, image_path = "generaltraining/hi_g"):
        while True:
            try:
                a, b = identify_image(image_path)
                break
            except ImageNotFoundException:
                continue
        return a, b

    def check_choice_event(self):
        while True:
            try:
                a, b = identify_image("generaltraining/hi_g")
                return a, b, "choice_event"
            except ImageNotFoundException:
                try:
                    a, b = identify_image("generaltraining/training")
                    return None, None, "training"
                except ImageNotFoundException:
                    pass

    def wait_text(self, text: str, region=None):
        """Wait for the text to appear in the specified region."""
        while True:
            self.screen_reader.capture_screen(region=region)
            detected_text = self.screen_reader.detect_text_in_image("test/screenshot.png", region)
            if text in detected_text:
                return True
            time.sleep(0.5)
        
    def new_year_event(self):
        logger.info(f"Turn {self.turn}: Check for new year event.")
        a, b = self.wait_choice_event()
        logger.info(f"Turn {self.turn}: New year event detected.")
        if self.turn == 30:
            click_true(a, b + 82 * 1, self.cfg["wait_time"]["_check_special_"])   # second choice is energy
        else:
            click_true(a, b + 82 * 0, self.cfg["wait_time"]["_check_special_"])   # first choice is energy
    
    def inspiration_event(self):
        self.wait_text("go")
        #FIXME: click to GO position

    def URA_training(self):
        """
        Train like in normal day and race without event after"""
        ...
    
    def _manual_race(self):
        ...
    
    def _check_race_event(self):
        ...
    
    def train_horse(self):
        self._check_mainrace()  

        # Training concentrate from here
        self._infirmary()       

        if self.turn in self.cfg["manual_race_day"]:
            self._manual_race()
            self._check_race_event()

        self._check_energy()

        mood_score = 3 if self._check_mood() else 0

        self._check_training(mood_score)
        # self._trouble_shoot()  # Check if inheriting event or connection error happens.

    def _trouble_shoot(self, racemode=0):   #Don't use yet
        if test_image("generaltraining/InsufficientFans"):
            self.click(1490, 520, 2)
        elif test_image("generaltraining/ConnectionError"):
            self.click(1625, 485, 2)
        elif test_image("generaltraining/RaceRecommendation"):
            self.click(1560, 635, 2)
        if racemode:
            pass
        elif test_image("generaltraining/DollGame"):
            for i in range(3):
                self.click(1550, 640, 3.5)
            self.click(1550, 620, 2)
        elif test_image("generaltraining/Inheriting"):
            self.click(self.cfg["trouble_shoot"]["inheriting"], 10)
            logger.info(f"Turn {self.turn}: Inheriting event detected, click to continue.")
            raise ContinueException
        else:
            try: 
                click_image("generaltraining/Next")
            except ImageNotFoundException:
                pass

    def _check_multiq(self):
        """Obtain support card special events (that do not choose green) and check for them then normal events."""
        a, b, event = self.check_choice_event()
        if event == "training":
            logger.info(f"Turn {self.turn}: No choice event, training UI detected.")
            return
        else:
            logger.info(f"Turn {self.turn}: Find choice event.")
            self.__check_special__(a, b)

    def __check_special__(self, a: float, b: float):
        """Handle clicking for special events.
        
        You really should not call this function alone."""

        self.screen_reader.capture_screen(region=(self.x, self.y, self.w, self.h))

        # Text region
        event_region = self.cfg["event_capture"]["event_text"]
        top, left = event_region["top_left"]
        bottom, right = event_region["bottom_right"]

        event_name = self.screen_reader.detect_text_in_image("test/screenshot.png", (top, left, bottom, right))      
        logger.info(f"Turn {self.turn}: Event name detected: {event_name}")

        if event_name in self.special_events:
            choice = self.special_events[event_name]["selectable"]
            if choice:
                click_true(a, b + 82 * (choice - 1), self.cfg["wait_time"]["_check_special_"])
            logger.info(f"Turn {self.turn}: Special event {event_name} detected, choice {choice} selected.")
        else:
            click_true(a, b, self.cfg["wait_time"]["_check_multiq"])  
            logger.info(f"Turn {self.turn}: Special event {event_name} not found in special events, choose green option.")


    def __update_friendship__(self, supportcard: SupportCard, rg, confi = 0.999):
        """Check the friendship bar of a support card"""
        if supportcard.friendship:
            pass  # Do not check when already know that the friendship bar turned orange & maxed.
        else:
            r, g, b = pyautogui.pixel(1672*2, rg[1]+40)
            if (r-243)**2 + (g-177)**2 + (b-69)**2 < 72:
                supportcard.friendship = 1
                print(f"Orange bar identified for {supportcard}")  # Test for orange bar by pixel color
            else:
                try:
                    pyautogui.locateOnScreen("figures/generaltraining/friendship_max.png", region=(rg[0]-30, rg[1]+25, 60, 35), confidence=confi)
                    supportcard.friendship = 1
                    print(f"Max bar identified for {supportcard}")
                except ImageNotFoundException:
                    print(f"Empty relationship bar ({supportcard.friendship}) is identified for {supportcard}")
        
    def __friendship_bonus_score__(self, training_type: str, supportcards: tuple):
        """Check from unpresented supportcard list and add scores for each present support card. Once a support card is present,
        remove it from unpresented support card list."""
        sc = supportcards.copy()
        score = 0
        for j in sc:
            ti = test_image(f"tscard/{j.name}", returncoordinate=True)
            if ti:
                self.__update_friendship__(j, rg=ti)  # Check the friendship status of the support card.
                supportcards.remove(j)  # Remove the support card from unpresented support card list.
                score += j.score(training_type, 1)
        return score
    
    def _match_event(self, event_name: str):
        # Use jiwer to match event_name with self.list_event keys
        best_match = None
        best_score = float('inf')
        for key in self.list_event.keys():
            # Normalize both event_name and key before calculating WER
            norm_event_name = jiwer.RemovePunctuation()(event_name.lower())
            norm_key = jiwer.RemovePunctuation()(key.lower())
            score = jiwer.wer(norm_event_name, norm_key)
            if score < best_score:
                best_score = score
                best_match = key
        return best_match


    def _check_mainrace(self):
        if self.turn not in self.race_day:
            return
        
        _, _ = self.wait_choice_event("generaltraining/RaceMain")

        logger.info(f"Turn {self.turn}: Following main agenda to race")
        self.click(self.cfg["root"]["daily_training"]["race_day"], self.cfg["wait_time"]["_check_mainrace"]["register"])
        self.click(self.cfg["lobby_ui"]["race_enter"], self.cfg["wait_time"]["_check_mainrace"]["register"])
        self.click(self.cfg["lobby_ui"]["race_confirm_button"], self.cfg["wait_time"]["_check_mainrace"]["event_wait"])

        #FIXME: make function control the style of the horse here.

        _, _ = self.wait_choice_event("generaltraining/Result")
        self.nclick(self.cfg["lobby_ui"]["view_result_button"], 3, self.cfg["wait_time"]["_check_mainrace"]["result_button"])
        self.nclick(self.cfg["lobby_ui"]["race_button"], 3, self.cfg["wait_time"]["_check_mainrace"]["race_button"])
        self.nclick(self.cfg["lobby_ui"]["next_button"], 2, self.cfg["wait_time"]["_check_mainrace"]["next_button"])

        #FIXME: add goal complete check ?

        raise ContinueException

    def _infirmary(self):
        if test_image("generaltraining/Infirmary", confi=0.80):  # Go to the infirmary to treat
            self.click(self.cfg["wait_time"]["infirmary"], self.cfg["wait_time"]["_check_mainrace"]["register"])
            time.sleep(4)
            logger.info(f"Turn {self.turn}: Call an ambulance.")
            raise ContinueException
        else:
            logger.debug(f"Turn {self.turn}: Status good today.")
            pass

    def __raise_mood__(self):
        if test_image(f"generaltraining/Recreation", confi=0.90):
            self.click(self.cfg["root"]["daily_training"]["recreation"], 0.5)
            logger.info(f"Turn {self.turn}: Raise mood by recreation.")
        else:  # for summer training.
            self.click(1450, 580)
        time.sleep(self.cfg["wait_time"]["_raise_mood_"])
    
    def __date_event__(self):
        time.sleep(10)
        self.screen_reader.capture_screen(region=(self.x, self.y, self.w, self.h))

        # Text region
        event_region = self.cfg["event_capture"]["event_text"]
        top, left = event_region["top_left"]
        bottom, right = event_region["bottom_right"]

        event_name = self.screen_reader.detect_text_in_image("test/screenshot.png", (top, left, bottom, right))      

        a, b, event = self.check_choice_event()

        if event_name in self.data_event:
            choice = self.special_events[event_name]["selectable"]
            if choice:
                click_true(a, b + 82 * (choice - 1), self.cfg["wait_time"]["_check_special_"])
            logger.info(f"Turn {self.turn}: Special event {event_name} detected, choice {choice} selected.")
        else:
            return
        

    def _check_mood(self):
        """Always spend turn to raise mood when below good, and return mood score 3 for good, 0 for great."""
        bad_mood = ("Awful", "Bad", "Normal")
        if self.turn == 0:
            logger.info(f"Turn {self.turn}: First turn, no mood check.")
            return 0  # Let it train for the first turn to use some energy.
        for i in bad_mood:
            if test_image(f"generaltraining/{i}", confi=0.85):
                self.__raise_mood__()
                self.__date_event__()
                raise ContinueException
            else:
                pass
        
        if test_image(f"generaltraining/Good"):
            logger.info(f"Turn {self.turn}: Mood is GOOD, no need to raise mood.")
            return 1
        else:
            logger.info(f"Turn {self.turn}: Mood is GREAT, no need to raise mood.")
            return 0

    def _check_energy(self):
        if test_image("generaltraining/EnergyBar", confi=0.96): #FIXME: add rg
            logger.info(f"Turn {self.turn}: Energy bar safe.")
            pass
        else:
            logger.info(f"Turn {self.turn}: Energy bar low, rest.")
            self.click(self.cfg['root']['daily_training']['rest'])
            time.sleep(self.cfg["wait_time"]["_check_energy_"])
            raise ContinueException
    
    def __extra_training_event__(self):
        time.sleep(10)
        self.screen_reader.capture_screen(region=(self.x, self.y, self.w, self.h))

        # Text region
        event_region = self.cfg["event_capture"]["event_text"]
        top, left = event_region["top_left"]
        bottom, right = event_region["bottom_right"]

        event_name = self.screen_reader.detect_text_in_image("test/screenshot.png", (top, left, bottom, right))      
        if event_name != "extra training":
            logger.info(f"Turn {self.turn}: No extra training event detected, event name: {event_name}")
            return
        else:
            a, b = identify_image("generaltraining/hi_g")
            click_true(a, b + 81, self.cfg["wait_time"]["_check_extra_training_"])  # Click on the second option.
    
    def _check_training(self, mood_score: float):
        logger.debug(f"Turn {self.turn}: Check training options.")
        training_ls = ["speed", "stamina", "power", "guts", "wits"]
        unpresented_supportcardlist = list(self.cfg.supportcard)

        try:
            self.click(self.cfg["root"]["daily_training"]["training"], 2)
            score = self.cfg.training_priority + [mood_score]
            order = [(self.pre_trainoption + i)%5 for i in range(1, 6)]  # Avoid single cicking of previous option.

            for i in order:
                self.click([self.cfg["training_option"]["speed"][0] + 80*i, self.cfg["training_option"]["speed"][1]], 0)
                score[i] += self.__friendship_bonus_score__(training_ls[i], unpresented_supportcardlist) 
                score[i] += 0.3 * test_image("URA/Director") 
                score[i] += 0.3 * test_image("URA/Reporter") 
                print(f"The score under {i + 1}th training option is {score[i]}")
            max_index = score.index(max(score))
            if max_index == 5:
                self.click(self.cfg["root"]["back_button"], 1)  # Click back
                self.__raise_mood__()
                raise ContinueException
            else:
                self.nclick([self.cfg["training_option"]["speed"][0] + max_index*80, self.cfg["training_option"]["speed"][1]], 4, self.cfg["wait_time"]["_check_training_"])
                self.pre_trainoption = max_index
                logger.info(f"Turn {self.turn}: Training {training_ls[max_index]} with score {score[max_index]}.")
                self.__extra_training_event__()
                raise ContinueException
        except ImageNotFoundException as e:
            print(e)
            pass

def identify_image(name="Sweep Tosho", confidence=0.9):
    """Identify the required png. 
    
    Return the true central coordinate of the image.
    If no image is identified, it will raise
    pyautogui.ImageNotFoundException."""
    l, t, w, h = pyautogui.locateOnScreen(f"figures_lap/{name}.png", confidence=confidence)
    # print(l, t, w, h)
    return (l+w/2, t+h/2)

def test_image(name: str, confi = 0.90, rg = None):
    """Return 1 if image is present, and 0 vice versa.
    
    rg, area of scanning, expects a tuple (left, top, width, height).
    If rg is None, scan the entire screen."""
    try:
        if rg is None:
            pyautogui.locateOnScreen(f"figures_lap/{name}.png", confidence=confi)
        else:
            pyautogui.locateOnScreen(f"figures_lap/{name}.png", confidence=confi, region=rg)
        return 1
    except ImageNotFoundException:
        return 0

def test_images(*args: str, confi = 0.9, rg = None, logic = "or", dir="generaltraining/"):
    """Return 1 if images present following and & or logic."""
    ts = sum(test_image(dir + i, confi=confi, rg=rg) for i in args)
    if ts:
        if logic == "or":
            return 1
        elif logic == "and" and ts == len(args):
            return 1
        else:
            return 0
    else:
        return 0

def click_true(a: float, b: float, interval=0.5):
        """Click on the true x-y position on computer screen."""
        pyautogui.click(a, b)
        time.sleep(interval)

def click_image(name: str):
    """Click on the exact position of image.
    
    All image clicking should use this function,
    since the click function adjusts coordinate based on window position."""
    a, b = identify_image(name)
    click_true(a, b, 2)

def resize_game(name: str):
    """Resize the game window to a fixed size."""
    window_title = name
    window = gw.getWindowsWithTitle(window_title)[0]

    # Lấy kích thước hiện tại và tính tỉ lệ
    original_width, original_height = window.width, window.height
    aspect_ratio = original_width / original_height

    new_width = 1440
    new_height = int(new_width / aspect_ratio)

    # Áp dụng kích thước mới
    window.resizeTo(new_width, new_height)



if __name__ == "__main__":
    resize_game("Umamusume")

    URA = UmaGame(test=1)
    URA._start_game(1)
    # URA.train_horse_loop("Oguri Cup", default_supportcard, turn=1)