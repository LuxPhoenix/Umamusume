from control import *


# Coordinates of icons
agree_term = (1630, 635)
change_country = (1650, 410)
country_OK = (1620, 520)
ok2 = (1620, 485)

def reroll():
    """Reroll for Kitasan Black!"""
    x = UmaGame(test=0)
    x.nclick(1560, 640, 2)
    time.sleep(4)
    x.nclick(agree_term[0], agree_term[1], 2)
    x.click(change_country[0], change_country[1])
    x.click(country_OK[0], country_OK[1])
    x.click(ok2[0], ok2[1])
    """
    Then input your birthday, name, etc.

    Then go to gacha page and pull.
    """


if __name__ == "__main__":
    reroll()  # Not implementable by pyautogui.
