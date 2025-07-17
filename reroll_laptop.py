import pyautogui
from pyautogui import ImageNotFoundException
import time
from builtins import Exception
import pygetwindow as gw
import json
from utils.logger import Logger
import math
import win32gui
import win32con

logger = Logger.get_logger()

# Get the screen size
screen_width, screen_height = pyautogui.size()  # Size in mouse functions' format, different from locate.

class UmaException(Exception):
    pass

class ContinueException(Exception):
    time.sleep(2)
    print("Continue to next turn.")
    pass

class UmaReroll:
    """Everything integrated."""

    def __init__(self, config:dict = None, test: bool = 1):
        """Adjust the coordinate system according to the device.
        
        self.xy records the coordinate of the topleft corner of the game window
        in the new device (self.xy[0], self.xy[1]),
        while self.xy[2], self.xy[3] are the amplification in width & height."""
        self.style = None
        self.pre_trainoption = None

        self.x, self.y, self.w, self.h, self.c = self._settings_config()  # Get the window position and size.
        self.pos_dict = self.get_pos_dict()  # Get the position dictionary.

    def _settings_config(self):
        window_title = "Umamusume"
        window = gw.getWindowsWithTitle(window_title)[0]

        # Lấy kích thước hiện tại và tính tỉ lệ
        original_width, original_height = window.width, window.height
        aspect_ratio = original_width / original_height

        new_width = 1280
        new_height = int(new_width / aspect_ratio)

        # Áp dụng kích thước mới
        window.resizeTo(new_width, new_height)


        with open('reroll_config.json', 'r', encoding='utf-8') as file:
            cfg = json.load(file)
        return (window.left, window.top, new_width, new_height, cfg)

    def get_pos_dict(self):
        """Get the position dictionary from the config file."""
        with open("reroll_config.json", "r", encoding="utf-8") as f:
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
    
    def click(self, coord: tuple, interval=2):
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

    def reroll_loop(self):
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
        self.click(self.c["menu"]["step1"])
        self.click(self.c["menu"]["terms1"])
        self.click(self.c["menu"]["terms2"])
        self.click(self.c["menu"]["confirm"])
        
        self.click(self.c["region"]["change"])
        self.click(self.c["region"]["ok1"])
        self.click(self.c["region"]["ok2"])

        self.click(self.c["age_confirm"]["click_point"])
        pyautogui.write(self.c["age_confirm"]["value"])
        self.click(self.c["age_confirm"]["ok3"], 5)

        self.click(self.c["skip_turtorial"], 3)

        self.click(self.c["trainer_registration"]["click_point"])
        pyautogui.write(self.c["trainer_registration"]["name"])
        self.nclick(self.c["trainer_registration"]["register"], 2, 1.5)
        self.click(self.c["trainer_registration"]["confirm"], 10)

        self.nclick(self.c["game"]["skip"], 8, 1.5)
        self.nclick(self.c["game"]["skip"], 2, 2.5)
        self.click(self.c["game"]["close1"])
        self.click(self.c["game"]["close2"])
        self.click(self.c["game"]["present"], 5)
        self.click(self.c["game"]["collect_all"], 2)
        self.click(self.c["game"]["close3"])

        self.click(self.c["banner"]["open"])
        self.click(self.c["banner"]["next"], 3, 1.5)
        self.click(self.c["banner"]["x10"])
        for i in range (7):
            self.click(self.c["banner"]["scout"])
            self.click(self.c["banner"]["skip"], 4, 1)
            self.click(self.c["banner"]["scout_again"])

        self.click(self.c["banner"]["close4"], 2)
        self.c

        return

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
                click_true(a, b, self.c["wait_time"]["_check_multiq"])  
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
        #FIXME: make this function that can choose special events's choice.
        x = 0
        for i in self.special_events:
            if test_image(f"tscard/{i}"):
                click_image("generaltraining/hi_y")
                print("Special choice selected.")
                x = 1
                time.sleep(self.c["wait_time"]["_check_special_"])
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
        self.click(self.c["root"]["daily_training"]["race_day"], self.c["wait_time"]["_check_mainrace"]["register"])
        self.click(self.c["lobby_ui"]["race_enter"], self.c["wait_time"]["_check_mainrace"]["register"])
        self.click(self.c["lobby_ui"]["race_confirm_button"], self.c["wait_time"]["_check_mainrace"]["event_wait"])

        #FIXME: make function control the style of the horse here.
        # if self.style == "front":
        #     self.nclick(self.c["lobby_ui"]["strategy_button"], 2, 1)  # change to front style. 
        #     self.click(self.c["lobby_ui"]["confirm_button"], 5)
        #     self.style = "changed"
        # else:
        #     pass

        if test_image("generaltraining/Result"):
            self.nclick(self.c["lobby_ui"]["view_result_button"], 3, self.c["wait_time"]["_check_mainrace"]["result_button"])
            self.nclick(self.c["lobby_ui"]["race_button"], 3, self.c["wait_time"]["_check_mainrace"]["race_button"])
            self.nclick(self.c["lobby_ui"]["next_button"], 2, self.c["wait_time"]["_check_mainrace"]["next_button"])
        else:
            raise NotImplementedError
        raise ContinueException

    def _infirmary(self):
        if test_image("generaltraining/Infirmary", confi=0.80):  # Go to the infirmary to treat
            print(f"Use turn {self.turn} to heal.")
            self.click(self.c["wait_time"]["infirmary"], self.c["wait_time"]["_check_mainrace"]["register"])
            time.sleep(4)
            logger.info(f"Turn {self.turn}: Call an ambulance.")
            raise ContinueException
        else:
            logger.debug(f"Turn {self.turn}: Status good today.")
            pass

    def __raise_mood__(self):
        if test_image(f"generaltraining/Recreation", confi=0.90):
            self.click(self.c["root"]["daily_training"]["recreation"], 0.5)
            logger.info(f"Turn {self.turn}: Raise mood by recreation.")
        else:  # for summer training.
            self.click(1450, 580)
        time.sleep(self.c["wait_time"]["_raise_mood_"])

    def _check_mood(self):
        """Always spend turn to raise mood when below good, and return mood score 3 for good, 0 for great."""
        bad_mood = ("Awful", "Bad", "Normal")
        if self.turn == 1:
            logger.info(f"Turn {self.turn}: First turn, no mood check.")
            return 0  # Let it train for the first turn to use some energy.
        for i in bad_mood:
            if test_image(f"generaltraining/{i}", confi=0.85):
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

def activate_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Khôi phục cửa sổ nếu minimized
        win32gui.SetForegroundWindow(hwnd)  # Focus cửa sổ
        return True
    return False

if __name__ == "__main__":
    resize_game("Umamusume")

    URA = UmaReroll(test=1)
    # URA._team_trial()
    # URA.remove_expired_followers(15)
    URA._start_game(1)
    URA.train_horse_loop("Oguri Cup", default_supportcard, turn=1)