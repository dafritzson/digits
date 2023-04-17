"""Main application for running all parts Digits and interacting with the user."""
import random
import sys
from time import sleep
from typing import Dict

from digits_app.src.constants import CLUES, DIFFICULTY, INSTRUCTIONS
from digits_app.src.database_builder import MapsDatabaseBuilder
from digits_app.src.utility_methods import load_map_file


class Digits:
    """Main class for defining flow of the game."""

    def __init__(
        self,
        num_digits: int = 6,
        answer: int = None,
        rebuild_db: bool = False,
        solved: bool = False,
        difficulty: str = None,
        map_files: Dict = None,
        debug: bool = False,
    ) -> None:
        """Generates clues for the provided number or a random one with the provided
        number of digits.

        Optionally runs the database builder and solver.
        Map files can be provided or will automatically load from `maps_db`.
        Difficulty can be provided or it will prompt the user to choose one.

        Args:
            num_digits: Number of digits in the desired mystery number
            answer: Provided number for the answer
            rebuild_db: Whether or not to rebuild the maps database
            solved: Whether or not to provide filtered clues based on difficulty level
            difficulty: Level of difficulty to use if playing solved.
        """
        self.num_digits = num_digits
        self.min = None
        self.max = None
        self.difficulty = difficulty
        self.answer = answer
        self.map_files = map_files or self.load_map_files()
        if rebuild_db:
            MapsDatabaseBuilder(self.min, self.max, self.difficulty)
        self.clues = None

    @staticmethod
    def load_map_files():
        """Load all map pkl files for all difficulties and clue types.

        Returns:
            Map file dictionaries keyed by difficulty and clue type
        """
        paths = {}
        map_files = {}
        for difficulty in DIFFICULTY.keys():
            paths[difficulty] = MapsDatabaseBuilder.get_maps_paths(CLUES, difficulty)
            map_files.setdefault(difficulty, {})
            for key in paths[difficulty]:
                map_files[difficulty].setdefault(key, {})
                map_files[difficulty][key] = load_map_file(difficulty, key)

        return map_files

    def generate_answer(self, digits: int) -> int:
        """Generate a random number in the range of provided number of digits.

        Args:
            digits: Number of digits in the desired mystery number.

        Returns:
            Random integer in valid range of provided number of digits.
        """
        self.min = 1 * 10 ** (digits - 1)
        self.max = 1 * 10 ** (digits) - 1
        return random.randint(self.min, self.max)

    @staticmethod
    def delay_print(
        msg: str, delay: float = 0.04, newline: bool = True, overwrite: bool = False
    ):
        """Prints a character to the console with a delay in between each character

        Args:
            msg: Message to print
            delay: Delay (s) between each character
            newline: Whether or not to print a new line at the end of the message
        """
        for char in msg:
            sys.stdout.write(char)
            sys.stdout.flush()
            sleep(delay)
        if overwrite:
            sys.stdout.write("\r")
        elif newline:
            sys.stdout.write("\n")

        sys.stdout.flush()

    def answer_prompt(self, debug=False) -> int:
        """Message to display the hidden number to the user at the start of the game"""
        if debug:
            answer = int(input("Give me the answer: "))
        else:
            self.num_digits = int(input("How many digits? ") or self.num_digits)
            answer_chars = ["_" for _ in range(self.num_digits)]
            answer = self.generate_answer(self.num_digits)
            starter = "I'm thinking of a number......"
            self.delay_print(starter)
            sleep(1.0)
            blank_answer = " ".join(answer_chars)
            self.delay_print(blank_answer, delay=0.25)

        return answer

    def difficulty_prompt(self) -> str:
        """Message to see if user wants to select a difficulty"""
        difficulty = input(
            "Select a difficulty or leave blank for random selection (easy/medium/hard): "
        ).lower()
        if difficulty not in DIFFICULTY:
            self.delay_print(
                "That's not a valid difficulty. I'll choose one for you.",
            )
            return list(DIFFICULTY.keys())[random.randint(0, len(DIFFICULTY) - 1)]
        return difficulty

    def end_prompt(self) -> bool:
        """Message to see if user wants to play again"""
        answer = input("Would you like to play again? ")
        return True if answer in ["y", "Y", "yes", "Yes", "yeah", "Yeah"] else False


if __name__ == "__main__":
    print(INSTRUCTIONS)
    Digits.delay_print("Loading...", newline=False, overwrite=True)
    map_files = Digits.load_map_files()
    while True:
        digits = Digits(
            answer=None,
            rebuild_db=False,
            solved=True,
            difficulty=None,
            map_files=map_files,
            debug=False,
        )
        if not digits.end_prompt():
            break
        sys.stdout.write("------------------------------------\n")
        sys.stdout.flush()
