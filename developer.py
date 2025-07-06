"""This module contains functions to help make the script for the developer."""
from control import *


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
