"""Clue generator application for any given number."""
from typing import Callable, Dict, List, Tuple, Type

import numpy as np
from constants import CLUES
from utility_methods import num_to_digits

import clues.clue as c
import clues.clue_map as cm


# TODO: Can refactor this to use the standardized naming of ClueMap classes
class ClueGenerator:
    """Container for all clue generation methods"""

    def __init__(self, number: int, difficulty: str) -> None:
        """Initialize all possible clues for a given number

        Args:
            number: Target answer
            difficulty: Clue difficulty
        """
        self.target = number
        self.difficulty = difficulty
        self.digits = num_to_digits(number)
        self.clues, self.num_maps = self.generate_clues()

    def generate_clues(
        self,
    ) -> Tuple[Dict[str, List[Type[c.Clue]]], Dict[Type[cm.ClueMapBase], List]]:
        """Generate all clues. Pulls method config data from the constants file

        Returns:
            all_clues: List of generated Clue objects
        """
        all_clues = {}
        maps = {}
        for clue, _kwargs in CLUES.items():
            for kwargs in _kwargs:
                new_clues, clue_map = getattr(self, f"generate_{clue}_clues")(**kwargs)
                key = kwargs.get("attribute") or clue
                all_clues[key] = new_clues
                maps[str(clue_map)] = clue_map.num_map
        return all_clues, maps

    def generate_multiples_clues(
        self, limits: Dict[str, Dict[str, int]] = None
    ) -> Tuple[List[str], Type[cm.ClueMapBase]]:
        """Generate clues from the multiples map

        Args:
            limit: Maximum factor size to include in clues.
                (Defaults to 4 because "x digit is 5 times y digit" is a giveaway)

        Returns:
            multiples_clues: Human-readable clues

        """
        limit = None if not limits else limits[self.difficulty].get("length")
        mcm = cm.MultiplesClueMap(self.digits, limit)
        map = mcm.num_map
        multiples_clues = []

        multiples_exist = np.any(map)
        for i, factors in enumerate(map):
            for j, dig in enumerate(factors):
                if 0 < dig <= limit or dig == -1:
                    clue = c.MultipleClue(
                        self.digits, factor=j, multiple=i, multiplier=dig
                    )
                    multiples_clues.append(clue)

        if not multiples_exist:
            multiples_clues.append("None of my digits are multiples of each other")

        return multiples_clues, mcm

    def generate_total_sum_clues(self) -> Tuple[List[str], Type[cm.ClueMapBase]]:
        """Generate clues for digits that have notable relation to sums of other digits"""
        clues = []
        scm = cm.TotalSumClueMap(self.digits)
        for dig, comp in scm.comparisons.items():
            clues.append(c.TotalSumClue(self.digits, dig, comp))
        return clues, scm

    def generate_even_clues(self) -> Tuple[List[str], Type[cm.ClueMapBase]]:
        """Generate clues about how many digits are even or odd"""
        clues = []
        eocm = cm.EvenClueMap(self.digits)
        clues.append(c.EvenClue(self.digits, eocm.num_even))
        return clues, eocm

    def generate_order_clues(self) -> Tuple[List[str], Type[cm.ClueMapBase]]:
        """Generate clues if the digits are in ascending or descending order"""
        clues = []
        ocm = cm.OrderClueMap(self.digits)
        clues.append(c.OrderClue(self.digits, ocm.ascending, ocm.descending))
        return clues, ocm

    def generate_partials_clues(
        self,
        prop_func: Callable,
        attribute: str,
        combo_size: int = 2,
    ) -> Tuple[List[str], Type[cm.ClueMapBase]]:
        """Generates clues for partial sums and products.
        E.g. 'X' digit is the product of digits 'Y' and 'Z'

        Args:
            prop_func: The function used to evaluate the group of digits
            attribute: Used to build the name of the formatting method
                e.g. 'partial_sums' to use the method format_partial_sums_clue()

        """
        clues = []
        pcm = cm.PartialsClueMap(self.digits, prop_func, attribute, combo_size)
        if any(pcm.num_map):
            for i, combos in enumerate(pcm.num_map):
                for combo in combos:
                    clues.append(
                        c.PartialsClue(
                            self.digits,
                            target_idx=i,
                            f1_idx=combo[0],
                            f2_idx=combo[1],
                            partial_type=attribute,
                        )
                    )
        else:  # Handle the case where there are no partial combinations
            clues.append(  # Clue is that there are no valid combinations
                c.PartialsClue(
                    self.digits,
                    target_idx=None,
                    f1_idx=None,
                    f2_idx=None,
                    partial_type=attribute,
                )
            )
        return clues, pcm

    def generate_special_properties_clues(
        self,
        prop_func: Callable,
        attribute: str,
        limits: Dict[str, Dict[str, int]] = None,
    ) -> Tuple[List[str], Type[cm.ClueMapBase]]:
        """Generates clues about all digits or combinations of digits have special characterists
        e.g. The number is prime or part of the Fibonacci sequence"""
        clues = []
        limit = None if not limits else limits[self.difficulty].get("length")
        stm = cm.SpecialPropertiesClueMap(
            self.digits, prop_func=prop_func, attribute=attribute, limit=limit
        )
        for special_digs in stm.num_map:
            clues.append(c.SpecialPropertiesClue(self.digits, attribute, special_digs))
        if len(stm.num_map) == 0:
            clues.append(c.SpecialPropertiesClue(self.digits, attribute, None))
        return clues, stm
