import pyautogui
from pyautogui import ImageNotFoundException
import time
from builtins import Exception

# Get the screen size
screen_width, screen_height = pyautogui.size()  # Size in mouse functions' format, different from locate.
x0, y0 = 1426.5, 185.5  # Coordinate of topleft corner on my macbook.
ww0, wh0 = 248.0, 500.5 # width and height of window on my macbook.
all_special_events = {"Sweep Tosho spe": ["wonderful_mistake"], "Super Creek sta": [], "Special Week spe": [], "Mayano Top Gun sta": [], "Gold City spe": [], "Eishin Flash spe": []}
default_supportcard = ("Sweep Tosho spe", "Super Creek sta", "Special Week spe", "Mayano Top Gun sta", "Gold City spe", "Eishin Flash spe")
ts_rg = (3300, 400, 100, 560)

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
            config = {"x0": 1426.5, "y0": 185.5, "ww0": 248.0, "wh0": 500.5}
        self.c = config
        self.screen_width, self.screen_height = pyautogui.size()  # Currently unused.
        if test:  # If test is true, conduct screen adjustment.
            a, b = identify_image("tlcorner")
            c, d = identify_image("brcorner")
            self.xy = (a, b, (c - a)/config["ww0"], (d - b)/config["wh0"])
            self.test = 1 
        else:
            self.test = 0

    def _coordinate_for_click(self, a: float, b: float):
        """Adjust the true coordinate to the relative position on my macbook."""
        if self.test:
            a1 = self.xy[0] + (a - self.c["x0"])*self.xy[2]
            b1 = self.xy[1] + (b - self.c["y0"])*self.xy[3]
        else:
            a1, b1 = a, b  # If window on topright corner of my screen, do not conduct screen adjustment.
        return a1, b1

    def click(self, a: float, b: float, interval=0.5):
        """Click on the x-y position on computer screen.

        The position is set to be the coordinate on my macbook,
        with the game window on top right corner from iphone 15 mirroring.
        For other devices and window, it will adjust the clicking position accordingly.
        The a, b therefore is only relative, and are not the actual pixel."""
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

    def _start_game(self, mode: bool):
        """Starting game from home screen."""
        self.nclick(1500, 400, 2)
        self.click(1650,630, 7)
        if mode:  # To continue a game.
            self.click(1640,520, 5)
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
        


    def train_horse_loop(self, name: str, supportcard: tuple = None):
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
        -> if mood is good: record and pass, with score 4.5
        -> if mood is great: pass

        5. check turn number, if at important time, attend g1 race at that time. If not then just pass

        6. check energy:
        -> if below 40, always rest -> turn += 1
        -> else pass

        7. check if training label is present:
        -> if true: check five training options and calculate scores for each (a head has base score 1, if relationship bar empty + 1, if friendship training + 2.5)
        (director and reporter both + 0.5, speed has base bonus + 1, stamina and power + 0.5, gut - 2, wit 0)

        calculate the highest score (together with mood if recorded) and choose the one. If multiple highest score use rng. -> turn += 1
        """
        self.turn = 1
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

        for i in range(75):
            try:
                self.train_horse(name, supportcard)
            except ContinueException:
                self.turn += 1
                continue

    def train_horse(self, name: str, supportcard: tuple = None):
        if supportcard is None:  # Load default support cards.
            supportcard = default_supportcard
        self._trouble_shoot()  # Check if inheriting event or connection error happens.
        self._check_multiq()
        self._check_mainrace()
        self._infirmary()
        mood_score = 4.5 if self._check_mood() else 0
        self._check_race(name)
        self._check_energy()
        self._check_training(supportcard, mood_score)

    def _trouble_shoot(self):
        if test_image("generaltraining/Inheriting"):
            self.click(1550, 580, 7)
            raise ContinueException
        else:
            pass

    def _check_multiq(self):
        """Obtain support card special events (that do not choose green) and check for them then normal events."""
        try: 
            for i in range(3):  # Adding the loop to met situations with consecutive multiple choose events.
                a, b = identify_image("generaltraining/hi_g")
                self.__check_special__()
                click_true(a, b, 4.5)
        except ImageNotFoundException:
            pass
        except UmaException:
            pass

    def __check_special__(self):
        """Handle clicking for special events.
        
        You really should not call this function alone."""
        x = 0
        for i in self.special_events:
            try:
                identify_image(f"tscard/{i}")
                click_image("generaltraining/hi_y")
                x = 1
                time.sleep(2.5)
                break
            except ImageNotFoundException:
                continue
        if x:
            raise UmaException("Special event detected.")

    def _check_mainrace(self):
        try: 
            click_image("generaltraining/RaceMain")
        except ImageNotFoundException:

            return None
        print("Following main agenda to race this turn.")
        self.click(1610, 620, 1)
        self.click(1610, 520, 7.5)
        if test_image("generaltraining/Front", confi=0.99):
            pass
        else:
            self.nclick(1635, 455, 2, 1)  # change to front style. 
            self.click(1620, 520, 5)
        if test_image("generaltraining/Result"):
            self.click(1500, 660, 5)
            self.nclick(1565, 660, 6, 4.5)
        else:
            raise NotImplementedError
        raise ContinueException

    def _infirmary(self):
        if test_image("generaltraining/Infirmary", confi=1):  # Go to the infirmary to treat
            print("Use this turn to heal.")
            self.click(1470, 640)
            self.nclick(1620, 480, 2)
            time.sleep(4)
            raise ContinueException
        else:
            pass

    def _check_mood(self):  # Finish later
        bad_mood = ("Awful", "Bad", "Normal")
        for i in bad_mood:
            if test_image(f"generaltraining/{i}"):
                self.click(1560, 640)
                self.nclick(1630, 490, 2)
                time.sleep(5)
                raise ContinueException
            else:
                pass
        if test_image(f"generaltraining/Good"):
            return 3  # I will change it to 4.5 once I add detection for rainbow.
        else:
            return 0
    
    def _check_race(self, name):  # Finish later
        pass

    def _check_energy(self):
        if test_image("generaltraining/EnergyBar", confi=0.99):
            pass
        else:
            print("Use this turn to rest.")
            self.click(1450, 586)
            self.nclick(1620, 480, 2)
            time.sleep(4)
            raise ContinueException
    
    def _check_training(self, supportcard, mood_score: float):
        try:
            click_image("generaltraining/Training")
            score = [1.5, 0.6, 0.5, -1, 0, mood_score]
            order = [(self.pre_trainoption + i)%5 for i in range(1, 6)]  # Avoid single cicking of previous option.
            for i in order:
                self.click(1450 + 50*i, 620, 0)
                score[i] += sum(test_image(f"tscard/{j}", rg=ts_rg) for j in supportcard)
                score[i] += 0.5 * test_image("URA/Director", rg=ts_rg)
                score[i] += 0.5 * test_image("URA/Reporter", rg=ts_rg)
                print(f"The score under {i + 1}th training option is {score[i]}")
            max_index = score.index(max(score))
            print(max_index)
            if max_index == 5:
                self.click(1440, 684, 1)  # Click back
                self.click(1560, 640)  # Recover mood for this turn.
                self.nclick(1630, 490, 2)
                print("Use this turn to recover mood.")
                time.sleep(5)
                raise ContinueException
            else:
                self.nclick(1450 + max_index * 50, 620, 2)
                self.pre_trainoption = max_index
                print("Use this turn to train")
                time.sleep(4)
        except ImageNotFoundException:
            pass


def identify_image(name="Sweep Tosho"):
    """Identify the required png. 
    
    Return the true central coordinate of the image.
    If no image is identified, it will raise
    pyautogui.ImageNotFoundException."""
    l, t, w, h = pyautogui.locateOnScreen(f"figures/{name}.png", confidence=0.9)
    # print(l, t, w, h)
    return (l/2+w/4, t/2+h/4)

def test_image(name: str, confi = 0.9, rg = None):
    """Return 1 if image is present, and 0 vice versa.
    
    rg, area of scanning, expects a tuple (left, top, width, height).
    If rg is None, scan the entire screen."""
    try:
        if rg is None:
            pyautogui.locateOnScreen(f"figures/{name}.png", confidence=confi)
        else:
            pyautogui.locateOnScreen(f"figures/{name}.png", confidence=confi, region=rg)
        return 1
    except ImageNotFoundException:
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


if __name__ == "__main__":
    URA = UmaGame(test=0)
    # URA._team_trial()
    # URA.remove_expired_followers(30)
    # URA._start_game(1)
    # URA.train_horse_loop("Gold Ship", default_supportcard)
    print(test_image("Test Label2", rg=(2690, 880, 200, 200)))

