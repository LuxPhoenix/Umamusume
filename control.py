import pyautogui
from pyautogui import ImageNotFoundException
import time
from builtins import Exception
from math import e
from horse_info import *

# Get the screen size
screen_width, screen_height = pyautogui.size()  # Size in mouse functions' format, different from locate.
x0, y0 = 1431.0, 133.5  # Coordinate of topleft corner on my macbook.
ww0, wh0 = 242.0, 553.5 # width and height of window on my macbook.
ts_rg = (3300, 400, 100, 560)
rest_bar = (3050, 365, 70, 24)  # Region of locate function for resting judgement.
racemain_bar = (3150, 1230, 74, 60)  # 1580, 620 is actual left top for race bar.
insufficient_fans_bar = (3050, 710, 360, 400)  # Remainder of insufficient fans pop-up.
teamrace_bar = (3000, 960, 300, 180)  # Indicator of teamrace label.
race_bar = {3220, 1290, 80, 80}

class UmaException(Exception):
    pass


class ContinueException(Exception):
    pass


class UmaGame:
    """Everything integrated."""

    def __init__(self, config:dict = None, test: bool = 1):
        """Adjust the coordinate system according to the device.
        
        self.xy records the coordinate of the topleft corner of the game window
        in the new device (self.xy[0], self.xy[1]),
        while self.xy[2], self.xy[3] are the amplification in width & height."""
        if config is None or len(config) != 4:
            config = {"x0": x0, "y0": y0, "ww0": ww0, "wh0": wh0}
        self.co = config
        self.screen_width, self.screen_height = pyautogui.size()  # Currently unused.
        if test:  # If test is true, conduct screen adjustment.
            c, b = identify_image("trcorner")
            a, d = identify_image("blcorner")
            self.xy = (a, b, (c - a)/config["ww0"], (d - b)/config["wh0"])
            self.test = 1 
        else:
            self.test = 0

    def _coordinate_for_click(self, a: float, b: float):
        """Adjust the true coordinate to the relative position on my macbook."""
        if self.test:
            a1 = self.xy[0] + (a - self.co["x0"])*self.xy[2]
            b1 = self.xy[1] + (b - self.co["y0"])*self.xy[3]
        else:
            a1, b1 = a, b  # If window on topright corner of my screen, do not conduct screen adjustment.
        return a1, b1

    def click(self, a: float, b: float, interval=0.5):
        """Click on the x-y position on computer screen.

        The position is set to be the coordinate on my macbook,
        with the game window on top right corner from iphone 15 mirroring.
        For other devices and window, it will adjust the clicking position accordingly.
        The a, b therefore is only relative, and are not the actual pixel.
        
        t is duration of pressing the mouse."""
        a1, b1 = self._coordinate_for_click(a, b)
        pyautogui.click(a1, b1)
        time.sleep(interval)

    def nclick(self, a: float, b: float, n: int, interval=0.5):
        """Click by n times."""
        if n <= 1:
            self.click(a, b, interval)
        else:  # Reduce cost by only calculating a1, b1 once.
            a1, b1 = self._coordinate_for_click(a, b)
            for i in range(n):
                pyautogui.click(a1, b1)
                time.sleep(interval)

    def test_image(self, name: str, confi = 0.9, rg = None):
        """Return 1 if image is present, and 0 vice versa.
        
        rg, area of scanning, expects a tuple (left, top, width, height).
        If rg is None, scan the entire screen."""
        try:
            if rg is None:
                pyautogui.locateOnScreen(f"figures/{name}.png", confidence=confi)
            else:
                a, b, c, d = rg
                a1, b1 = self._coordinate_for_click(a/2, b/2)  # Keep it for now
                rg1 = (int(a1*2), int(b1*2), c, d)
                pyautogui.locateOnScreen(f"figures/{name}.png", confidence=confi, region=rg1)
            return 1
        except ImageNotFoundException:
            return 0    

    def test_images(self, *args: str, confi = 0.9, rg = None, logic = "or", dir="generaltraining/"):
        """Return 1 if images present following and & or logic."""
        ts = sum(self.test_image(dir + i, confi=confi, rg=rg) for i in args)
        if ts:
            if logic == "or":
                return 1
            elif logic == "and" and ts == len(args):
                return 1
            else:
                return 0
        else:
            return 0

    def _start_game(self, character: HorseGirl = Oguri_Cup, mode: bool = 0):
        """Starting game from home screen."""
        self.nclick(1500, 400, 2)
        self.click(1650,630, 7)
        if mode:  # To continue a game.
            self.click(1640,520, 5)
        else:  # To start a new game.
            self.click(1550, 610)  # To character page
            click_image(f"characterselect/{character.name}")  # Select character.
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
                    click_image(f"friendsupcard/{character.friend_support}")  # Select friend support card.
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

        for i in range(5):
            self.click(1500, 500, 5)  # Click Team Race
            self.click(1550, 400, 7)
            self.click(1550, 620, 2)
            self.click(1610, 510, 5)
            while not self.test_image("TeamRace", rg=teamrace_bar):
                self.nclick(1580, 650, 10, 0.1)
            if i == 4:
                self.nclick(1550, 680, 3)
                self.click(1580, 650)
                self.click(1550, 680, 3)
                break
    
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
        


    def train_horse_loop(self, character: HorseGirl = Daiwa_Scarlet, style: str = "front", turn = 1):
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
        self.c = character

        self.click(1550, 240)  # Make sure screen is accessible.

        while self.turn <= 80:
            try:
                self.train_horse()
            except ContinueException:
                self.turn += 1
                time.sleep(4)
                continue

    def train_horse(self):
        self._check_multiq()
        self._check_mainrace()
        self._infirmary()
        self._check_race()  # Put this priority below infirmary since health is always the first, haha.
        mood_score = 3 if self._check_mood() else 0
        self._check_energy()
        self._check_training(mood_score)
        self._trouble_shoot()  # Check if inheriting event or connection error happens.

    def _trouble_shoot(self, racemode=0):
        if self.test_image("generaltraining/InsufficientFans"):
            self.click(1490, 520, 2)
        elif self.test_image("generaltraining/ConnectionError"):
            self.click(1625, 485, 2)
        elif self.test_image("generaltraining/RaceRecommendation"):
            self.click(1560, 635, 2)
        # Skip following check during race trouble shooting.
        if racemode:
            pass
        elif self.test_image("generaltraining/DollGame"):
            for i in range(3):
                self.click(1550, 640, 3.5)
            self.click(1550, 620, 2)
        elif self.test_image("generaltraining/Inheriting"):
            self.click(1550, 580, 7)
            print(f"Inheriting event at turn {self.turn}.")
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
                print("Choose green choice.")
        except ImageNotFoundException:
            pass
        except UmaException:
            pass

    def __check_special__(self):
        """Handle clicking for special events.
        
        You really should not call this function alone."""
        x = 0
        for i in self.c.special_events:
            if self.test_image(f"specialevents/{i}"):
                click_image("generaltraining/hi_y")
                print("Special choice selected.")
                x = 1
                time.sleep(2.5)
                break
        if x:
            raise UmaException("Special event detected.")

    def _check_mainrace(self):
        if self.test_images("RaceMain", "RaceURA", confi=0.98, rg=racemain_bar, dir="generaltraining/"):  #  or test_image("URA/RaceURA")
            self.click(1615, 625, 1)
        else:
            return None
        print(f"Following main agenda to race on turn {self.turn}.")
        self.click(1610, 620, 1)
        self.click(1610, 520, 7.5)
        if self.style == "front":
            self.nclick(1635, 455, 2, 1)  # change to front style. 
            self.click(1620, 520, 5)
            self.style = "changed"
        else:
            pass
        if self.test_image("generaltraining/Result"):
            self.click(1500, 660, 5)
            self.nclick(1565, 660, 6, 4.5)
        else:
            raise NotImplementedError
        raise ContinueException

    def _infirmary(self):
        if self.test_image("generaltraining/Infirmary", confi=0.9998):  # Go to the infirmary to treat
            print(f"Use turn {self.turn} to heal.")
            self.click(1470, 640)
            self.nclick(1620, 480, 2)
            time.sleep(4)
            raise ContinueException
        else:
            pass

    def __raise_mood__(self):
        if self.test_image(f"generaltraining/Rest", confi=0.99):
            self.click(1560, 640)
        else:  # for summer training.
            self.click(1450, 580)
        print(f"Use turn {self.turn} to raise mood.")
        self.nclick(1630, 490, 2)
        time.sleep(5)

    def _check_mood(self):
        """Always spend turn to raise mood when below good, and return mood score 3 for good, 0 for great."""
        bad_mood = ("Awful", "Bad", "Normal")
        if self.turn == 1:
            return 0  # Let it train for the first turn to use some energy.
        for i in bad_mood:
            if self.test_image(f"generaltraining/{i}"):
                self.__raise_mood__()
                raise ContinueException
            else:
                pass
        if self.test_image(f"generaltraining/Good"):
            return 1
        else:
            return 0
    
    def _check_race(self, rl: dict = None):
        """Attend race according to turns recorded in RaceTable for the character."""
        if rl is None:
            rl = self.c.race_table
        if self.turn in rl.keys():
            while self.test_image("generaltraining/Races", rg=race_bar):
                self.click(1615, 625, 4)
            try:
                click_image(f"URA/races/{rl[self.turn]}")
            except ImageNotFoundException:
                self._trouble_shoot(1)
                self._check_multiq()
            self.click(1620, 625, 4)
            self.click(1620, 520, 8)
            print(f"Use turn {self.turn} to attend {rl[self.turn]}.")
            if self.test_image("generaltraining/Result"):
                self.click(1500, 660, 5)
                self.nclick(1565, 660, 4, 4.5)
            else:
                raise NotImplementedError
            raise ContinueException


    def _check_energy(self):
        if not self.test_image(f"generaltraining/Training", confi=0.99):
            pass
        elif self.test_image("generaltraining/EnergyBar", confi=0.98, rg=rest_bar):
            pass
        else:
            print(f"Use turn {self.turn} to rest.")
            self.click(1450, 586)
            self.nclick(1620, 480, 2)
            time.sleep(4)
            raise ContinueException
    
    def _check_training(self, mood_score: float):
        try:
            click_image("generaltraining/Training")
            score = self.c.training_priority + [mood_score]
            order = [(self.pre_trainoption + i)%5 for i in range(1, 6)]  # Avoid single cicking of previous option.
            for i in order:
                self.click(1450 + 50*i, 620, 0)
                score[i] += self.__friendship_bonus_score__(1)
                score[i] += 0.3 * self.test_image("URA/Director", rg=ts_rg)
                score[i] += 0.3 * self.test_image("URA/Reporter", rg=ts_rg)
                print(f"The score under {i + 1}th training option is {score[i]}")
            max_index = score.index(max(score))
            training_ls = ["Speed", "Stamina", "Power", "Guts", "Wits"]
            if max_index == 5:
                self.click(1440, 684, 1)  # Click back
                self.__raise_mood__()
                raise ContinueException
            else:
                self.nclick(1450 + max_index * 50, 620, 2)
                self.pre_trainoption = max_index
                print(f"Use turn {self.turn} to train {training_ls[max_index]}")
                raise ContinueException
        except ImageNotFoundException:
            pass

    def __friendship_bonus_score__(self, simple: bool = 0):
        if simple:
            amplifier = 1
        else:
            amplifier = 1.2 - 0.7/(1 + e**(-0.18*(self.turn - 35)))
        return amplifier * sum(self.test_image(f"tscard/{j}", rg=ts_rg) for j in self.c.supportcard)


def identify_image(name: str):
    """Identify the required png. 
    
    Return the true central coordinate of the image.
    If no image is identified, it will raise
    pyautogui.ImageNotFoundException."""
    l, t, w, h = pyautogui.locateOnScreen(f"figures/{name}.png", confidence=0.9)
    # print(l, t, w, h)
    return (l/2+w/4, t/2+h/4)


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


if __name__ == "__main__":
    URA = UmaGame(test=0)
    # URA._team_trial()
    # URA.remove_expired_followers(15)
    # URA._start_game(Daiwa_Scarlet, 0)
    URA.train_horse_loop(Maruzensky, turn=35)
