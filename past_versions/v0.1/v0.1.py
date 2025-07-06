"""This version only works on my macbook and does not contain actual training part."""


import pyautogui
from pyautogui import ImageNotFoundException
import time

screen_size = (2880, 1864)
pack_size = (1920, 1080)

def swup(a:float, b: float):
    return a/1920*2880*1.331, b/1920*2880*1.331

def swdown(a:float, b: float):
    return a/2880*1920/1.331, b/2880*1920/1.331

def click(a: float, b: float, interval=0.5):
    """Click on the x-y position on mac screen."""
    pyautogui.click(a, b)
    time.sleep(interval)

def nclick(a: float, b: float, num: int, interval=0.5):
    """Click by num times."""
    for i in range(max(1, num)):
        click(a, b, interval)

def identify_image(name="Sweep Tosho"):
    """Identify the required png. 
    
    Return the central coordinate in 1920*1080 framework.
    If no image is identified, it will raise
    pyautogui.ImageNotFoundException."""
    l, t, w, h = pyautogui.locateOnScreen(f"{name}.png", confidence=0.9)
    print(l, t, w, h)
    return swdown(l+w/2, t+h/2)


def start_game(mode: bool):
    """Starting game from home screen."""
    nclick(1500, 400, 2)
    click(1650,630, 7)
    if mode:  # To continue a game.
        click(1640,520)
    else:  # To start a new game.
        click(1550, 610)  # To character page
        click(1500, 420)  # Select Air groove
        click(1550, 610)  # Confirm
        click(1450, 450) 
        click(1500, 440)  # Select first parent
        click(1550, 610)  # Confirm
        click(1600, 450)
        click(1600, 440)  # Select second parent
        nclick(1550, 610, 2)  # Confirm
        click(1650, 420)  # Click on friend support card
        for i in range(25):
            try:
                a, b = identify_image("Sweep Tosho")
                print(a, b)
                click(a, b)
                break
            except ImageNotFoundException:
                click(1675, 550, 2)    
        click(1550, 610)  # Enter the game
        click(1640, 630, 5)
        click(1680, 670)  # Skip intro
        click(1640, 480, 2.5)
        click(1550, 520, 2.5)
        nclick(1510, 690, 2, 5)

def team_trial():
    """Conduct team trial from home screen, untill no stamina."""
    nclick(1500, 400, 2)
    click(1620, 680, 2)  # Click race
    click(1450, 500, 5)
    click(1500, 500, 5)
    for i in range(5):
        click(1550, 400, 7)
        click(1550, 620, 2)
        click(1610, 510, 5)
        nclick(1580, 650, 12, 4.5)
        if i == 4:
            nclick(1550, 680, 3)
            break
        nclick(1500, 650, 3, 5)
    

# start_game(0)
# team_trial()

