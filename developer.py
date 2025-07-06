"""This module contains functions to help make the script for the developer."""
from control import *


x0, y0 = identify_image("tlcorner")
x1, y1 = identify_image("brcorner")

print(x0, y0, x1, y1)
print(x1-x0, y1 - y0)