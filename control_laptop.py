import pyautogui
from pyautogui import ImageNotFoundException
import time
from builtins import Exception
import pygetwindow as gw
import json
from utils.logger import Logger

logger = Logger.get_logger()

# Get the screen size
screen_width, screen_height = pyautogui.size()  # Size in mouse functions' format, different from locate.
# x0, y0 = 1431.0, 133.5  # Coordinate of topleft corner on my macbook.
# ww0, wh0 = 242.0, 553.5 # width and height of window on my macbook.
all_special_events = {"Sweep Tosho spe": ["wonderful_mistake"], "Super Creek sta": [], "Special Week spe": [], "Mayano Top Gun sta": [], "Gold City spe": [], "Eishin Flash spe": [], "King Halo spe": [], "Bakushin spe": [], "Fine Motion wit": []}
default_supportcard = ("Sweep Tosho spe", "Super Creek sta", "Special Week spe", "Mayano Top Gun sta", "Gold City spe", "Eishin Flash spe", "Bakushin spe", "Fine Motion wit", "King Halo spe")
ts_rg = (3300, 400, 100, 560)
rest_bar = (3050, 365, 70, 24)  # Region of locate function for resting judgement.
racemain_bar = (3150, 1230, 74, 60)  # 1580, 620 is actual left top for race bar.
insufficient_fans_bar = (3050, 710, 160, 140)  # Remainder of insufficient fans pop-up.
RaceTable = {21: ("Keto Hai Junior", "Daily Hai Junior"), 
            23: ("Hanshin Juvenile", "Asahi Hai Futurity"),
            24: ("Hopeful S")
}
Oguri_RaceTable = {23: "Hanshin Juvenile", 24: "Hopeful S", 32: "Oka Sho", 35: "Japan Derby", 45: "Shuka Sho", 55: "Osaka hai", 58: "Tenno Sho Spring", 59: "Victoria Mile", 61: "Yasuda Kinen", 72: "Japan C"}

class UmaException(Exception):
    pass


class ContinueException(Exception):
    time.sleep(2)
    print("Continue to next turn.")
    pass


class UmaGame:
    """Everything integrated."""

    def __init__(self, config:dict = None, test: bool = 1):
        """Adjust the coordinate system according to the device.
        
        self.xy records the coordinate of the topleft corner of the game window
        in the new device (self.xy[0], self.xy[1]),
        while self.xy[2], self.xy[3] are the amplification in width & height."""
        # if config is None or len(config) != 4:
        #     config = {"x0": 1426.5, "y0": 185.5, "ww0": 248.0, "wh0": 500.5}
        # self.c = config
        self.screen_width, self.screen_height = pyautogui.size()  # Currently unused.
        self.style = None
        self.pre_trainoption = None
        # if test:  # If test is true, conduct screen adjustment.
        #     a, b = identify_image("tlcorner")
        #     c, d = identify_image("brcorner")
        #     self.xy = (a, b, (c - a)/config["ww0"], (d - b)/config["wh0"])
        #     self.test = 1 
        # else:
        #     self.test = 0

        self.x, self.y, self.w, self.h, self.c = self._settings_config()  # Get the window position and size.
        self.pos_dict = self.get_pos_dict()  # Get the position dictionary.

    def _settings_config(self):
        window_title = "Umamusume"
        window = gw.getWindowsWithTitle(window_title)[0]

        # Lấy kích thước hiện tại và tính tỉ lệ
        original_width, original_height = window.width, window.height
        aspect_ratio = original_width / original_height

        new_width = 1440
        new_height = int(new_width / aspect_ratio)

        # Áp dụng kích thước mới
        window.resizeTo(new_width, new_height)

        
        with open('dictionary.json', 'r', encoding='utf-8') as file:
            cfg = json.load(file)
        return (window.left, window.top, new_width, new_height, cfg)
    
    def get_pos_dict(self):
        """Get the position dictionary from the config file."""
        with open("dictionary.json", "r", encoding="utf-8") as f:
            pos_dict = json.load(f)
        return pos_dict

    def _coordinate_for_click(self, a: float, b: float):
        """Adjust the true coordinate to the relative position on my macbook."""
        if self.test:
            a1 = self.xy[0] + (a - self.c["x0"])*self.xy[2]
            b1 = self.xy[1] + (b - self.c["y0"])*self.xy[3]
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

    def _start_game(self, mode: bool):
        """Starting game from home screen."""
        self.nclick(self.pos_dict["menu"]["home"], 2)   # Double next
        self.click(1650,630, 7)
        if mode:  # To continue a game.
            self.click(self.pos_dict["career_menu"]["next"], 5)
        else:  # To start a new game.
            self.click(1550, 610)  # To character page
            self.click(1500, 420)  # Select Air groove
            self.click(1550, 610)  # Confirm
            self.click(1450, 450) 
            self.click(1500, 440)  # Select first parent
            self.click(1550, 610)  # Confirm
            self.click(1600, 450)
            self.click(1600, 440)  # Select second parent
            self.nclick(1550, 610, 2)  # Confirm
            self.click(1650, 420)  # Click on friend support card
            for i in range(25):
                try:
                    click_image("Sweep Tosho")
                    break
                except ImageNotFoundException:
                    self.click(1675, 550, 2)    
            self.click(1550, 610)  # Enter the game
            self.click(1640, 630, 5)
            self.click(1680, 670)  # Skip intro
            self.click(1640, 480, 2.5)
            self.click(1550, 520, 2.5)
            self.nclick(1510, 690, 2, 1.5)
            time.sleep(3.5)

    def _team_trial(self):
        """Conduct team trial from home screen, untill no stamina."""
        self.nclick(1500, 400, 3)
        self.click(1620, 680, 3)  # Click race
        self.click(1450, 500, 6)
        self.click(1500, 500, 5)
        for i in range(5):
            self.click(1550, 400, 7)
            self.click(1550, 620, 2)
            self.click(1610, 510, 5)
            self.nclick(1580, 650, 12, 4.5)
            if i == 4:
                self.nclick(1550, 680, 3)
                self.click(1580, 650)
                self.click(1550, 680, 3)
                break
            self.nclick(1500, 650, 5, 5)
    
    def remove_expired_followers(self, n: int = 10):
        """Remove followers that does not log in."""
        self.nclick(1500, 400, 2)
        self.click(1670, 130)
        self.click(1470, 300, 10)
        self.click(1550, 170)
        for i in range(n):
            self.click(1500, 200, 4)
            self.click(1470, 338, 3)
            self.click(1560, 480)
            self.click(1550, 630)
            self.nclick(1670, 583, 2)
        self.click(1550, 683, 3)
        


    def train_horse_loop(self, name: str, supportcard: tuple = None, style: str = "front", turn = 1):
        """Train the horse with following logic.

        conduct this loop, starting from turn 1:

        1. check if there is any multiple choose questions on screen (test if hi_g.png is present)
        -> if true: check if the event is recorded as special:
                -> if true: choose according to special event outcome
                -> if false: always choose the green option (top one)
        -> if false: pass

        2. check if the event-race label is present:
        -> if true: 
            add skills (not implemented)
            attend race (change style to front, and click on result if unlocked. if locked, go to game) -> turn += 1
        -> if false: pass

        3. check if infirmary is open:
        -> if true: go heal the uma -> turn += 1
        -> if false: pass

        4. check status of mood:
        -> if mood awful or bad or normal: entertainment directly -> turn += 1
        -> if mood is good: record and pass, with score 3
        -> if mood is great: pass

        5. check turn number, if at important time, attend g1 race at that time. If not then just pass

        6. check energy:
        -> if below 40, always rest -> turn += 1
        -> else pass

        7. check if training label is present:
        -> if true: check five training options and calculate scores for each (a head has base score 1, if relationship bar empty + 1, if friendship training + 2.5)
        (director and reporter both + 0.5, speed has base bonus + 1.5, stamina + 0.6, power + 0.5, gut - 0.8, wit 0)

        calculate the highest score (together with mood if recorded) and choose the one. If multiple highest score use rng. -> turn += 1
        """
        self.turn = turn
        self.style = style
        self.pre_trainoption = 0  # The default starting "previous" training is speed.
        if supportcard is None:  # Load default support cards.
            supportcard = default_supportcard
        s = []  # The part loads special event list.
        for i in supportcard:
                x = all_special_events[i] 
                if len(x) > 0:
                    for j in x:
                        s.append(j)
        self.special_events = s

        # self.click(1550, 240)  # Make sure screen is accessible.

        while self.turn <= 80:
            try:
                self.train_horse(name, supportcard)
            except ContinueException:
                self.turn += 1
                time.sleep(4)
                continue

    def train_horse(self, name: str, supportcard: tuple = None):
        if supportcard is None:  # Load default support cards.
            supportcard = default_supportcard
        self._check_multiq()    # 90%
        self._check_mainrace()  # 90%
        self._infirmary()       
        # self._check_race()  # Put this priority below infirmary since health is always the first, haha.
        mood_score = 3 if self._check_mood() else 0
        self._check_energy()
        self._check_training(supportcard, mood_score)
        self._trouble_shoot()  # Check if inheriting event or connection error happens.

    def _trouble_shoot(self, racemode=0):
        if test_image("generaltraining/InsufficientFans"):
            self.click(1490, 520, 2)
        elif test_image("generaltraining/ConnectionError"):
            self.click(1625, 485, 2)
        elif test_image("generaltraining/RaceRecommendation"):
            self.click(1560, 635, 2)
        # Skip following check during race trouble shooting.
        if racemode:
            pass
        elif test_image("generaltraining/DollGame"):
            for i in range(3):
                self.click(1550, 640, 3.5)
            self.click(1550, 620, 2)
        elif test_image("generaltraining/Inheriting"):
            self.click(self.c["trouble_shoot"]["inheriting"], 10)
            logger.info(f"Turn {self.turn}: Inheriting event detected, click to continue.")
            raise ContinueException
        else:
            try: 
                click_image("generaltraining/Next")
            except ImageNotFoundException:
                pass

    def _check_multiq(self):
        """Obtain support card special events (that do not choose green) and check for them then normal events."""
        try: 
            for i in range(3):  # Adding the loop to met situations with consecutive multiple choose events.
                a, b = identify_image("generaltraining/hi_g")
                self.__check_special__()
                click_true(a, b, 7.5)
            logger.info(f"Turn {self.turn}: Special event detected.")
        except ImageNotFoundException:  # No special event.
            logger.debug(f"Turn {self.turn}: No choice event.")
            pass
        except UmaException:
            logger.debug(f"Turn {self.turn}: Choice event detected but no special event.")
            pass

    def __check_special__(self):
        """Handle clicking for special events.
        
        You really should not call this function alone."""
        x = 0
        for i in self.special_events:
            if test_image(f"tscard/{i}"):
                click_image("generaltraining/hi_y")
                print("Special choice selected.")
                x = 1
                time.sleep(2.5)
                break
        if x:
            raise UmaException("Special event detected.")

    def _check_mainrace(self):
        if test_images("RaceMain", "RaceURA", confi=0.80, rg=None, dir="generaltraining/"):
            logger.info(f"Turn {self.turn}: Race day detected.")
        else:
            logger.debug(f"Turn {self.turn}: No main race today.")
            return
        
        logger.info(f"Turn {self.turn}: Following main agenda to race")
        self.click(self.c["root"]["daily_training"]["race_day"], 1)
        self.click(self.c["lobby_ui"]["race_enter"], 1.5)
        self.click(self.c["lobby_ui"]["race_confirm_button"], 10)

        #FIXME: make function control the style of the horse here.
        # if self.style == "front":
        #     self.nclick(self.c["lobby_ui"]["strategy_button"], 2, 1)  # change to front style. 
        #     self.click(self.c["lobby_ui"]["confirm_button"], 5)
        #     self.style = "changed"
        # else:
        #     pass

        if test_image("generaltraining/Result"):
            self.nclick(self.c["lobby_ui"]["view_result_button"], 3, 4.5)
            self.nclick(self.c["lobby_ui"]["race_button"], 6, 4.5)
            self.nclick(self.c["lobby_ui"]["next_button"], 2, 4.5)
        else:
            raise NotImplementedError
        raise ContinueException

    def _infirmary(self):
        if test_image("generaltraining/Infirmary", confi=0.95):  # Go to the infirmary to treat
            print(f"Use turn {self.turn} to heal.")
            self.click(self.c["root"]["daily_training"]["infirmary"])
            self.nclick(1620, 480, 2)
            time.sleep(4)
            logger.info(f"Turn {self.turn}: Call an ambulance.")
            raise ContinueException
        else:
            logger.debug(f"Turn {self.turn}: Status good today.")
            pass

    def __raise_mood__(self):
        if test_image(f"generaltraining/Recreation", confi=0.90):
            self.click(self.c["root"]["daily_training"]["recreation"])
            logger.info(f"Turn {self.turn}: Raise mood by recreation.")
        else:  # for summer training.
            self.click(1450, 580)
        time.sleep(5)

    def _check_mood(self):
        """Always spend turn to raise mood when below good, and return mood score 3 for good, 0 for great."""
        bad_mood = ("Awful", "Bad", "Normal")
        if self.turn == 1:
            logger.info(f"Turn {self.turn}: First turn, no mood check.")
            return 0  # Let it train for the first turn to use some energy.
        for i in bad_mood:
            if test_image(f"generaltraining/{i}"):
                self.__raise_mood__()
                raise ContinueException
            else:
                pass
        
        if test_image(f"generaltraining/Good"):
            logger.info(f"Turn {self.turn}: Mood is GOOD, no need to raise mood.")
            return 1
        else:
            logger.info(f"Turn {self.turn}: Mood is GREAT, no need to raise mood.")
            return 0
    
    def _check_race(self, rl: dict = {}):
        """Attend race according to turns recorded in RaceTable for the character."""
        # if self.turn in rl.keys():
        #     self.click(1615, 625, 2)
        #     try:
        #         click_image(f"URA/races/{rl[self.turn]}")
        #     except ImageNotFoundException:
        #         self._trouble_shoot(1)
        #         self._check_multiq()
        #     self.click(1620, 625, 2)
        #     self.click(1620, 520, 8)
        #     print(f"USe turn {self.turn} to attend {rl[self.turn]}.")
        #     if test_image("generaltraining/Result"):
        #         self.click(1500, 660, 5)
        #         self.nclick(1565, 660, 4, 4.5)
        #     else:
        #         raise NotImplementedError
        #     raise ContinueException
        pass

    def _check_energy(self):
        # if not test_image(f"generaltraining/Training", confi=0.99):
        #     print("No training label, no energy check.")
        #     pass
        # elif test_image("generaltraining/EnergyBar", confi=0.98, rg=rest_bar):
        if test_image("generaltraining/EnergyBar", confi=0.95):
            logger.info(f"Turn {self.turn}: Energy bar safe.")
            # self.click(self.c['root']['daily_training']['rest'])
            pass
        else:
            logger.info(f"Turn {self.turn}: Energy bar low, rest.")
            self.click(self.c['root']['daily_training']['rest'])
            # self.nclick(1620, 480, 2)
            time.sleep(4)
            raise ContinueException
    
    def _check_training(self, supportcard, mood_score: float):
        logger.debug(f"Turn {self.turn}: Check training options.")
        # print(1/0)
        try:
            self.click(self.c["root"]["daily_training"]["training"], 2)
            score = [1.5, 0.6, 0.5, -0.8, 0, mood_score]
            order = [(self.pre_trainoption + i)%5 for i in range(1, 6)]  # Avoid single cicking of previous option.
            for i in order:
                self.click([self.c["training_option"]["speed"][0] + 80*i, self.c["training_option"]["speed"][1]], 0)
                score[i] += sum(test_image(f"tscard/{j}") for j in supportcard) #NOTE: remove rg=ts_rg
                score[i] += 0.3 * test_image("URA/Director") 
                score[i] += 0.3 * test_image("URA/Reporter") #NOTE: remove rg=ts_rg
                print(f"The score under {i + 1}th training option is {score[i]}")
            max_index = score.index(max(score))
            training_ls = ["Speed", "Stamina", "Power", "Guts", "Wits"]
            if max_index == 5:
                self.click(self.c["root"]["back_button"], 1)  # Click back
                self.__raise_mood__()
                raise ContinueException
            else:
                self.nclick([self.c["training_option"]["speed"][0] + max_index*80, self.c["training_option"]["speed"][1]], 4, 1)
                self.pre_trainoption = max_index
                # print(f"Use turn {self.turn} to train {training_ls[max_index]}")  
                logger.info(f"Turn {self.turn}: Training {training_ls[max_index]} with score {score[max_index]}.")
                raise ContinueException
        except ImageNotFoundException as e:
            print(e)
            pass


def identify_image(name="Sweep Tosho"):
    """Identify the required png. 
    
    Return the true central coordinate of the image.
    If no image is identified, it will raise
    pyautogui.ImageNotFoundException."""
    l, t, w, h = pyautogui.locateOnScreen(f"figures_lap/{name}.png", confidence=0.9)
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
    # URA._team_trial()
    # URA.remove_expired_followers(15)
    URA._start_game(1)
    URA.train_horse_loop("Oguri Cup", default_supportcard, turn=1)
