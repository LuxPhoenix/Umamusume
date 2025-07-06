import pyautogui
from pyautogui import ImageNotFoundException
import time


# Get the screen size
screen_width, screen_height = pyautogui.size()  # Size in mouse functions' format, different from locate.
x0, y0 = 1426.5, 185.5  # Coordinate of topleft corner on my macbook.
ww0, wh0 = 248.0, 500.5 # width and height of window on my macbook.


class UmaGame:
    """Everything integrated."""

    def __init__(self, config:dict = None):
        """Adjust the coordinate system according to the device.
        
        self.xy records the coordinate of the topleft corner of the game window
        in the new device (self.xy[0], self.xy[1]),
        while self.xy[2], self.xy[3] are the amplification in width & height."""
        if config is None or len(config) != 4:
            config = {"x0": 1426.5, "y0": 185.5, "ww0": 248.0, "wh0": 500.5}
        self.c = config
        self.screen_width, self.screen_height = pyautogui.size()  # Currently unused.
        a, b = identify_image("tlcorner")
        c, d = identify_image("brcorner")
        self.xy = (a, b, (c - a)/config["ww0"], (d - b)/config["wh0"])

    def _coordinate_for_click(self, a: float, b: float):
        """Adjust the true coordinate to the relative position on my macbook."""
        a1 = self.xy[0] + (a - self.c["x0"])*self.xy[2]
        b1 = self.xy[1] + (b - self.c["y0"])*self.xy[3]
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
            self.click(1640,520)
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
        self.nclick(1500, 400, 2)
        self.click(1620, 680, 2)  # Click race
        self.click(1450, 500, 5)
        self.click(1500, 500, 5)
        for i in range(5):
            self.click(1550, 400, 7)
            self.click(1550, 620, 2)
            self.click(1610, 510, 5)
            self.nclick(1580, 650, 12, 4.5)
            if i == 4:
                self.nclick(1550, 680, 3)
                self.click(1580, 650)
                break
            self.nclick(1500, 650, 3, 5)


def identify_image(name="Sweep Tosho"):
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
    URA = UmaGame()
    # URA._start_game(0)
    URA._team_trial()


