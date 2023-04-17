"""Constant values and settings."""
import os
from typing import Dict

from sympy import is_perfect, isprime

from src.utility_methods import check_product, check_sum, is_fibonacci

INDEX_STRING_MAP: Dict[int, str] = {
    0: "1st",
    1: "2nd",
    2: "3rd",
}
INDEX_STRING_MAP.update({i: str(i + 1) + "th" for i in range(3, 11)})
"""Map of 0-indexed keys to 1-indexed placement string"""

POS_RESPONSES = [
    "Wowowowow! Good job!",
    "Congratulations! You guessed correctly!",
    "Nice work! I love you!",
    "Well done, nerd.",
    "Impressive!",
    "Nice job! I'll get you next time.",
    "Wow! You're my hero!",
    "Showoff.",
    "Booyah!!",
]
"""Positive responses for guessing the number correctly"""

DIFFICULTY = {
    "easy": {
        "responses": [
            "Oh this is an easy one. You got this.",
            "I'll be disappointed if you don't get this one...",
            "This one is just a warm up...",
            "Sorry, this one isn't going to be much of a challenge for you...",
        ]
    },
    "medium": {
        "responses": [
            "Don't consider 3+ digit prime, fibonacci, or perfect number clues for this one."
        ]
    },
    "hard": {
        "responses": [
            "Oh man...this is a tough one...",
            "You might want to get a pen and paper out for this one...",
            "You might need Google for this one...",
            "This is a tough one...good luck.",
        ]
    },
}
"""Difficulties and their respective custom responses"""

CLUES = {
    "multiples": [
        {
            "limits": {
                "easy": {"length": 9},
                "medium": {"length": 4},
                "hard": {"length": 4},
            }
        }
    ],
    "total_sum": [{}],
    "special_properties": [
        {
            "prop_func": isprime,
            "attribute": "prime",
            "limits": {"easy": {"length": 1}, "medium": {"length": 2}, "hard": {}},
        },
        {
            "prop_func": is_perfect,
            "attribute": "perfect",
            "limits": {"easy": {"length": 1}, "medium": {"length": 2}, "hard": {}},
        },
        {
            "prop_func": is_fibonacci,
            "attribute": "fibonacci",
            "limits": {"easy": {"length": 1}, "medium": {"length": 2}, "hard": {}},
        },
    ],
    "even": [{}],
    "order": [{}],
    "partials": [
        {"prop_func": check_product, "attribute": "product"},
        {"prop_func": check_sum, "attribute": "sum"},
    ],
}
"""Clue types and their respective configuration settings"""

MAPS_DB = os.path.join(__package__, "src", "maps_db")
"""Path to the database of map files"""

INSTRUCTIONS = """
Can you guess what number I am?

You get to choose how many digits I contain.
I'll give you a few clues to help you make your guess.
Each clue contains a CAPITALIZED keyword. 
You may need to consider which clues of the provided keyword were NOT given to you to find the answer. 

There are three difficulty levels that you can choose. If you don't choose one, I'll
choose one at random for you:

    Easy
    - I'll give you more clues than you need.
    - Some clues may be dead giveaways. 
        (e.g. "My 1st digit DIVIDED by 7 equals my 2nd digit")
    - You only need to consider single-digit numbers when evaluating your clues.

    Medium
    - I'll only give you as many clues as you need.
    - If you are not given clues of a certain keyword, absent clues for that keyword should not be considered.
        (e.g. If you are not given any clues about PRIME numbers, then you shouldn't assume there are no PRIME digits)
    - No clues should be dead giveaways.
        (e.g. You won't be given a clue like "My 1st digit DIVIDED by 7 equals my 2nd digit", even if it is applicable)
    - You only need to consider up to double-digit numbers when evaluating clues.

    Hard
    - Same as medium mode, but you will need to consider all sized numbers when
    evaluating clues.
    - You may need a pencil and/or Google for this one.

"""
"""Opening instructions"""

BLANK_LINE = "                                                                   \r"
