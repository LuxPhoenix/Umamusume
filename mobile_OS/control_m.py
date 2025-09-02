import pyautogui
from pyautogui import ImageNotFoundException
import time
from builtins import Exception
from math import e
from horse_info_m import *
from numbers import Number

# sensible defaults
pyautogui.FAILSAFE = True

# scaling helpers
def _detect_scale(default_scale=None):
    if default_scale is None:
        shot = pyautogui.screenshot()
        return shot.width / pyautogui.size()[0]
    else:
        return default_scale

SCALE = _detect_scale()

# switch from actual and logical coordinates
def _fp(content, scalefactor=1):
    """Adjust the coordinate since pyautogui is fucked.
    
    scaleup: let scalefactor = 1
    scaledown: let scalefactor = -1"""
    if isinstance(content, Number):
        return int(content * SCALE**scalefactor)
    elif isinstance(content, tuple):
        return tuple(int(i*SCALE**scalefactor) for i in content)
    else:
        raise NotImplementedError(f"_fp not implemented for type {type(content)}.")

# Get the screen size
screen_width, screen_height = pyautogui.size()  # Size in mouse functions' format, different from locate.
x0, y0 = 1431.0, 133.5  # Coordinate of topleft corner on my macbook.
ww0, wh0 = 242.0, 553.5 # width and height of window on my macbook.
ts_rg = (1650, 200, 50, 280)
rest_bar = (1525, 182, 35, 12)  # Region of locate function for resting judgement.
racemain_bar = (1575, 615, 37, 30)  # 1580, 620 is actual left top for race bar.
insufficient_fans_bar = (1525, 355, 180, 200)  # Remainder of insufficient fans pop-up.
teamrace_bar = (1500, 480, 150, 90)  # Indicator of teamrace label.
race_bar = (1610, 645, 150, 150)
teamtrials_bar = (1445, 545, 200, 25)
teamrace_refresh_bar = (1660, 608, 45, 45)
RP_bar1 = (1566, 115, 35, 35)
home_bar = (1500, 650, 100, 60)
option_bar = (1650, 665, 45, 45)

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

    def click(self, a: float, b: float, interval=0.5, connecting_mode=False):
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

    def test_image(self, name: str, confi = 0.9, rg = None, returncoordinate = False):
        """Return 1 if image is present, and 0 vice versa.
        
        rg, area of scanning, expects a tuple (left, top, width, height).
        If rg is None, scan the entire screen."""
        try:
            if rg is None:
                x = pyautogui.locateCenterOnScreen(f"figures_m/{name}.png", confidence=confi)
            else:
                a, b, c, d = rg
                rg1 = _fp((*self._coordinate_for_click(a, b), c, d))
                x = pyautogui.locateCenterOnScreen(f"figures_m/{name}.png", confidence=confi, region=rg1)
            if returncoordinate:
                return _fp(x, -1)
            else:
                return 1
        except ImageNotFoundException:
            return 0 

    def wait_for(self, name: str, confi=0.9, rg=None, timeout=10.0, check_every=0.25, click=False, interval=0.5):
        """Wait until an image appears; return its center or None on timeout. Click the centre position if click is True."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            center = self.test_image(name, confi, rg, 1)
            if center:
                if click:
                    click_true(*center, interval)
                return center
            time.sleep(check_every)
        return None

    def wait_for_any(self, *args, logic="or", confi=0.9, rg=None, dir="generaltraining/", timeout=10.0, check_every=0.25):
        """Wait for any & all of the images in args appears before timeout; return 1 if so and 0 otherwise."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.test_images(*args, confi=confi, rg=rg, logic=logic, dir=dir):
                return 1
            time.sleep(check_every)
        return 0

    def clicks_until(self, position: tuple, name: str, confi=0.9, rg=None, timeout=10.0, check_every=0.1):
        """Click a position until an image appears."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            center = self.test_image(name, confi, rg, 1)
            if center:
                return 1
            self.click(*position, interval=check_every)
        return None

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

    def _team_trial(self):
            """Conduct team trial from home screen, until no stamina."""
            if self.wait_for("teamtrial/RP", rg=RP_bar1, confi=0.99, timeout=3) is None:
                print("No RP for team trials.")
                return None
            self.nclick(1500, 400, 3)
            self.click(1620, 680)  # Click race
            self.wait_for("teamtrial/TeamTrials", rg=teamtrials_bar, click=1)
            while self.wait_for("teamtrial/RP", rg=RP_bar1, confi=0.99, timeout=8):
                self.wait_for("teamtrial/TeamRace", rg=teamrace_bar, click=1)
                self.wait_for("refresh", rg=teamrace_refresh_bar)
                self.click(1550, 400)  # Click the second opponent.
                self.wait_for("generaltraining/next", rg=(1500, 600, 100, 35), click=1)
                self.click(1610, 510)
                while not self.test_image("teamtrial/TeamRace", rg=teamrace_bar):
                    self.nclick(1580, 650, 10, 0.1)
            self.wait_for("home", rg=home_bar, click=1)

    def _start_game(self, character: HorseGirl = Oguri_Cap, mode: bool = 0):
        """Starting game from home screen."""
        self.nclick(1500, 400, 2)
        if mode:  # To continue a game.
            self.click(1650,630, 2)
            self.click(1640,520, 5)
        else:  # To start a new game.
            self.click(1650,630, 9)
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
    
    def remove_expired_followers(self, n: int = 10):
        """Remove followers that does not log in."""
        self.nclick(1500, 400, 2)
        self.click(1670, 130)
        self.click(1470, 300, 10)
        self.click(1550, 170)
        for i in range(n):
            self.click(1500, 200, 5)
            self.click(1470, 338, 5)
            self.click(1560, 480)
            self.click(1550, 630)
            self.nclick(1670, 583, 2)
        self.click(1550, 683, 3)
        


    def train_horse_loop(self, character: HorseGirl = Daiwa_Scarlet, style: str = "front", turn = 1, hint_priority = 5):
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
        self.hint_priority = hint_priority
        if turn == 1:
            self.pre_trainoption = 0  # The default starting "previous" training is speed.
        else:
            self.pre_trainoption = 2  # Avoid hitting same option immediately. Rarely train guts so click guts first.
        self.c = character
        self.trouble_count = 0

        self.click(1550, 240)  # Make sure screen is accessible.

        while self.turn <= 80:
            try:
                self.train_horse()
            except ContinueException:
                self.turn += 1
                self.trouble_count = 0
                time.sleep(1)
                continue

    def train_horse(self):
        self._check_multiq()
        self._check_mainrace()
        self._infirmary()
        self._check_race()  # Put this priority below infirmary since health is always the first, haha.
        mood_score = 3 if self._check_mood() else 0
        if self._check_energy():
            self._check_training(mood_score)
        self._trouble_shoot()  # Check if inheriting event or connection error happens.

    def _trouble_shoot(self, racemode=0):
        self.trouble_count += 1
        if self.trouble_count >= 6:
            exit("Cannot resolve trouble, ending autoplay.")
        try: 
            click_image("generaltraining/Next")
            return 0
        except ImageNotFoundException:
            pass
        try:
            click_image("generaltraining/Cancel")
            return 0
        except ImageNotFoundException:
            pass
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
        elif self.test_image("generaltraining/Close"):
            click_image("generaltraining/Close")
        else:
            print("problem unresolved.")

    def _check_multiq(self):
        """Obtain support card special events (that do not choose green) and check for them then normal events."""
        try: 
            for i in range(3):  # Adding the loop to met situations with consecutive multiple choose events.
                a, b = identify_image("generaltraining/hi_g")
                # self.__check_special__()
                click_true(a, b)
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
                break
        if x:
            raise UmaException("Special event detected.")

    def _check_mainrace(self):
        if self.wait_for_any("RaceMain", "RaceURA", confi=0.98, rg=racemain_bar, dir="generaltraining/", timeout=2, check_every=0):
            self.click(1615, 625)
        else:
            return None
        print(f"Following main agenda to race on turn {self.turn}.")
        self.wait_for("generaltraining/Race", rg=(1580, 610, 100, 30), click=1)
        self.click(1620, 520)
        if self.style != "changed":
            time.sleep(7)
            self.nclick(1635, 455, 2, 1)  # change to front style. 
            self.click(1620, 520)
            self.style = "changed"
        else:
            pass
        if self.wait_for("generaltraining/Result", rg=(1456, 640, 100, 40), click=1) is None:
            raise NotImplementedError
        self.clicks_until((1565, 660), "generaltraining/Option", rg=option_bar, timeout=15)
        time.sleep(1.5)
        if self.turn >= 76:
            self.nclick(1565, 675, 4, 1.5)
        else:
            self.nclick(1565, 675, 8, 1.5)
        raise ContinueException

    def _check_skill(self):
        try:
            click_image("generaltraining/Skills", 1.5)
            for i in self.c.skill_set:
                pass  # Finish this part later
        except ImageNotFoundException:
            pass


    def _infirmary(self):
        if self.test_image("generaltraining/Infirmary", confi=0.9998):  # Go to the infirmary to treat
            print(f"Use turn {self.turn} to heal.")
            self.click(1470, 640)
            self.nclick(1620, 480, 2)
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
        self.pre_trainoption = 3

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
            if not (self.test_image("generaltraining/Races", rg=race_bar) or self.test_image(f"URA/races/{rl[self.turn]}")):
                print("Trouble shooting for race preparation...")
                self._check_multiq()
                self._trouble_shoot(1)
                self._check_race()
            self.wait_for("generaltraining/Races", rg=race_bar, click=1)
            self._trouble_shoot(1)
            if self.wait_for(f"URA/races/{rl[self.turn]}", click=1) is None:
                self.click(1560, 445)
                pyautogui.drag(0, 100, 1, button="left")
                click_image(f"URA/races/{rl[self.turn]}")
                print("Reclicking successful")
            else:
                print("Clicking successful")
            self.wait_for("generaltraining/Race", rg=(1580, 610, 100, 30), click=1)
            self.click(1620, 520)
            print(f"Use turn {self.turn} to attend {rl[self.turn]}.")
            self.wait_for("generaltraining/Result", rg=(1456, 640, 100, 40), click=1)
            self.clicks_until((1565, 660), "generaltraining/Option", rg=option_bar, timeout=15)
            raise ContinueException


    def _check_energy(self):
        if self.wait_for(f"generaltraining/Training", confi=0.99, timeout=3) is None:
            return 0
        elif self.test_image("generaltraining/EnergyBar", confi=0.98, rg=rest_bar):
            return 1
        else:
            print(f"Use turn {self.turn} to rest.")
            self.click(1450, 586)
            self.nclick(1620, 480, 2)
            raise ContinueException
    
    def _check_training(self, mood_score: float):
        training_ls = ["speed", "stamina", "power", "guts", "wits"]
        unpresented_supportcardlist = list(self.c.supportcard)
        if self.wait_for("generaltraining/Training", timeout=7, click=1) is None:
            return None
        score = self.c.training_priority + [mood_score]
        order = [(self.pre_trainoption + i)%5 for i in range(1, 6)]  # Avoid single cicking of previous option.
        for i in order:
            self.click(1450 + 50*i, 620, 0)
            score[i] += self.__friendship_bonus_score__(training_ls[i], unpresented_supportcardlist)
            score[i] += 0.3 * self.test_image("URA/Director", rg=ts_rg)
            score[i] += 0.3 * self.test_image("URA/Reporter", rg=ts_rg)
            if self.hint_priority:
                score[i] += self.hint_priority * self.test_image("generaltraining/inspiration", rg=ts_rg, confi=0.85)
            print(f"The score under {i + 1}th training option is {int(score[i]*100)/100}")
        max_index = score.index(max(score))
        if max_index == 5:
            self.click(1440, 684, 1)  # Click back
            self.__raise_mood__()
            raise ContinueException
        else:
            self.nclick(1450 + max_index * 50, 620, 2)
            self.pre_trainoption = max_index
            print(f"Use turn {self.turn} to train {training_ls[max_index]}")
            raise ContinueException

    def __update_friendship__(self, supportcard: SupportCard, rg, confi = 0.97):
        """Check the friendship bar of a support card"""
        if supportcard.friendship:
            pass  # Do not check when already know that the friendship bar turned orange & maxed.
        else:
            r, g, b = pyautogui.pixel(1672*SCALE, _fp(rg[1])+40)
            if (r-243)**2 + (g-177)**2 + (b-69)**2 < 72:
                supportcard.friendship = 1
                print(f"Orange bar identified for {supportcard}")  # Test for orange bar by pixel color
            else:
                try:
                    r1, g1 = _fp(rg)
                    pyautogui.locateOnScreen("figures_m/generaltraining/friendship_max.png", region=(r1-30, g1+25, 60, 35), confidence=confi)
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
            ti = self.test_image(f"tscard/{j.name}", rg=ts_rg, returncoordinate=True)
            if ti:
                self.__update_friendship__(j, rg=ti)  # Check the friendship status of the support card.
                supportcards.remove(j)  # Remove the support card from unpresented support card list.
                score += j.score(training_type, 1)
        return score


def identify_image(name: str):
    """Identify the required png. 
    
    Return the true central coordinate of the image.
    If no image is identified, it will raise
    pyautogui.ImageNotFoundException."""
    l, t, w, h = _fp(pyautogui.locateOnScreen(f"figures_m/{name}.png", confidence=0.9), -1)
    return (l+w/2, t+h/2)


def click_true(a: float, b: float, interval=0.5):
        """Click on the true x-y position on computer screen."""
        pyautogui.click(a, b)
        time.sleep(interval)


def click_image(name: str, interval=2):
    """Click on the exact position of image.
    
    All image clicking should use this function,
    since the click function adjusts coordinate based on window position."""
    a, b = identify_image(name)
    click_true(a, b, interval)



if __name__ == "__main__":
    URA = UmaGame(test=0)
    # URA._team_trial()
    # URA.remove_expired_followers(35)
    URA._start_game(Oguri_Cap3, 1)
    URA.train_horse_loop(Oguri_Cap3, turn=1)
    # print(URA.__friendship_bonus_score__("speed", list(Oguri_Cap3.supportcard)))
