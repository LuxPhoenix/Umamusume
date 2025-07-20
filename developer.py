"""This module contains functions to help make the script for the developer."""
from math import factorial


def probability_of_Kitasan(n: int, k: int, rounding: bool):
    """Calculates the probability of getting k kitasan black SSR out of n polls."""
    prob = factorial(n)/(factorial(k)*factorial(n-k)) * 0.005**k * (1-0.005)**(n-k)
    if rounding:
        return int(prob*1000)/1000
    else:
        return prob


if __name__ == "__main__":
   for i in range(5):
       print(f"The probability of getting {i} Kitasan Black SSR out of 200 polls is {probability_of_Kitasan(600, i, 1)}")
