"""Collection of utility methods."""
import math
import os
import pickle
from functools import wraps
from time import time
from typing import List


def bold(key: str) -> str:
    """Bolds a provided string"""
    return key.upper()
    # return "\033[1m{}\033[0m".format(key)


def is_fibonacci(num: int) -> bool:
    """Determines if the provided value is part of the Fibonacci sequence"""

    def _is_perfect_square(val: int):
        s = int(math.sqrt(val))
        return s * s == val

    return _is_perfect_square(5 * num * num + 4) or _is_perfect_square(
        5 * num * num - 4
    )


def check_sum(x: int, y: int, target: int) -> bool:
    """Evaluates sum of provided values"""
    return x + y == target


def check_product(x: int, y: int, target: int) -> bool:
    """Evaluates product of provided values"""
    return x * y == target


def num_to_digits(num: int) -> List[int]:
    """Convert number to a list of digits"""
    return [int(dig) for dig in str(num)]


def digits_to_num(digits: List[int]) -> int:
    """Convert number to a list of digits"""
    return int("".join([str(d) for d in digits]))


def timed(func):
    """Logs the amount of time taken to run a function"""

    @wraps(func)
    def wrap(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        # print(
        #     "Function: %r executed. Elapsed time: %2.3f sec"
        #     % (func.__name__, end - start)
        # )
        return result

    return wrap


def snake_to_camelcase(name: str) -> str:
    """Converts a snake_case variable name to CamelCase format"""
    words = name.split("_")
    return "".join(map(str.title, words))


def default_map_to_key(num_map: List):
    """Default conversion of a numeric map to a key for the pkl object"""
    return tuple(num_map)


@timed
def load_map_file(difficulty: str, key: str) -> pickle.OBJ:
    """Builds path of map file from difficulty and clue key

    Args:
        difficulty: Difficulty level
        key: Clue key (e.g. 'divide', 'prime', 'sum', etc.)

    Returns:
        Loaded map file as a pickle object
    """
    path = os.path.join(
        os.path.dirname(__file__), "maps_db", f"{difficulty}_{key}_maps.pkl"
    )
    with open(path, "rb") as file:
        return pickle.load(file)
