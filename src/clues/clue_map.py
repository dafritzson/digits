"""Classes for generating numeric maps for each clue type."""
import itertools
from abc import abstractmethod
from typing import Callable, Dict, List, Tuple

import numpy as np


class ClueMapBase:
    """Builds a map of clues for the provided digits.

    Each object's map will be iterated through in the `ClueGenerator` to generate each
    `Clue` object.
    """

    def __init__(self, digits: List[int]) -> None:
        """Sets the base attributes for the map."""
        self.num_map: List = []
        self.digits = digits

    def __repr__(self) -> str:
        """Representation of the map class for managing of objects."""
        return self.__class__.__name__

    @abstractmethod
    def build_clue(self):
        """Overwrite in child classes with custom functionality to build the map."""


class OrderClueMap(ClueMapBase):
    """Clue map for the Order clue type."""

    def __init__(self, digits: List[int]) -> None:
        """Sets the attributes for the Order clue map"""
        super().__init__(digits)
        self.ascending, self.descending, self.num_map = self.build_clue()

    def build_clue(self) -> Tuple[bool, bool, List[int]]:
        """Builds a number map based on if digits are in ascending or descending order.

        Returns:
            Ascending, descending, and number map representation.
        """
        ascending = all(cur <= next for cur, next in zip(self.digits, self.digits[1:]))
        descending = all(cur >= next for cur, next in zip(self.digits, self.digits[1:]))
        num_map = [int(ascending), int(descending)]
        return ascending, descending, num_map


class TotalSumClueMap(ClueMapBase):
    """Clue map for the Total Sum clue type."""

    def __init__(self, digits: List[int]) -> None:
        """Sets the attributes for the Order clue map."""
        super().__init__(digits)
        self.sum = sum(digits)
        self.comparisons, self.num_map = self.build_clue()

    def build_clue(self) -> Tuple[Dict[int, str], List[str]]:
        """Generate clues for digits that have notable relation to the total sum of
        other digits.

        Returns:
            comparisons: String representations of sum comparisons for each digit
            comp_map: Integer representations of sum comparisons for each digit"""

        comparisons = {}
        comp_map = []
        for i, val in enumerate(self.digits):
            if val > self.sum - val:
                comparisons[i] = "greater than"
                comp_map.append(1)
                continue
            elif val == self.sum - val:
                comparisons[i] = "equal to"
                comp_map.append(0)
            else:
                comp_map.append(-1)

        return comparisons, comp_map


class EvenClueMap(ClueMapBase):
    """Clue map for the Even clue type."""

    def __init__(self, digits: List[int]) -> None:
        """Sets the attributes for the Even clue map."""
        super().__init__(digits)
        self.num_even: int = 0
        self.num_map = self.build_clue()

    def build_clue(self):
        """Creates a number map of whether or not each digit is even."""
        num_map = [1 if val % 2 == 0 else 0 for val in self.digits]
        self.num_even = num_map.count(1)
        return num_map


class MultiplesClueMap(ClueMapBase):
    """Clue map for the Multiples clue type."""

    def __init__(self, digits: List[int], limit: int) -> None:
        """Sets the attributes for the Multiples clue map.

        Args:
            digits: Number represented as a list of its digits.
            limit: Limit of the multiples to consider when building the map.
        """
        super().__init__(digits)
        self.limit = limit
        self.num_map = self.build_clue(self.digits, self.limit)

    def build_clue(self, digits: List[int], limit: int) -> np.ndarray:
        """Build a map of the factors that relate two digits where one digit is a
        multiple of the other.

        e.g. For the number 23462
            >>> digits = [2, 3, 4, 6, 2]
            >>> build_multiples_map(digits)
            [
                [0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0],
                [2, 0, 0, 0, 2],
                [3, 2, 0, 0, 3],
                [1, 0, 0, 0, 0]
            ]

        Args:
            digits: List of each digit in the target number.
            limit: Max multiple that will be considered.

        Returns:
            map: Map of each digit's factors relative to other digits.
        """
        d = np.array(digits)

        # Ignore zero division warnings
        with np.errstate(divide="ignore", invalid="ignore"):
            # Broadcast from 1xN to NxN matrix
            # Outer divide by its original 1xN elements
            map = d[:, np.newaxis] / d

        # Edge case where multiple zeros exist in the number
        # E.g. 10203
        # TODO: Vectorize this
        zeros = np.where(d == 0)[0]
        if len(zeros) > 1:
            map_copy = map.tolist()
            for i, row in enumerate(map_copy):
                row = [
                    -1 if i in zeros and j in zeros and i != j else val
                    for j, val in enumerate(row)
                ]
                map_copy[i] = row
            map = np.array(map_copy)

        # Set all floats to 0
        map[map != map.astype(int)] = 0

        map[map > limit] = 0

        # Set all self-referencing factors to 0 using the identity matrix
        map[map == np.identity(len(d))] = 0

        # Convert all floats to integers to avoid needing to cast in clue formatting
        map = map.astype(int)

        return map


class SpecialPropertiesClueMap(ClueMapBase):
    """Clue map for the Special Properties clue type.

    Examples: "prime", "fibonacci", "perfect".
    """

    def __init__(
        self, digits: List[int], prop_func: Callable, attribute: str, limit: int = None
    ) -> None:
        """Sets the attributes for the Special Properties clue map.

        Args:
            digits: Number represented as a list of its digits.
            prop_func: Property function to call on the number.
            attribute: Special property (e.g. "prime", "fibonacci").
            limit: Max length of combination of digits to apply the property check to.
        """
        super().__init__(digits)
        self.prop_func = prop_func
        self.attribute = attribute
        self.limit = limit or len(self.digits)
        self.num_map = self.build_clue()

    def __repr__(self) -> str:
        """String representation of the instance including the attribute name"""
        return self.attribute.capitalize() + super().__repr__()

    def build_clue(self) -> List[int]:
        """Builds a map of all digit combinations that have the special attribute.

        Returns:
            List of digits and combinations of digits that satisfy the `self.prop_func`
            check.

        Example:
            If digits 1, 3, and 4 have the special attribute, the list returned will be
            [11, 33, 44].
            If digits 2, and the combination of digits 1-4 have the special attribute,
            the list returned will be [14, 22].
            If digits 2, the combination 1-4, and combination 4-6 have the attribute,
            the list returned will be [14, 22, 46].
        """
        map = []
        for i, _ in enumerate(self.digits):
            limit = min(len(self.digits), i + self.limit)
            for j in range(i, limit):
                # TODO: Maybe replace this logic with itertools.permutations?
                cand = int("".join(str(dig) for dig in self.digits[i : j + 1]))
                if self.prop_func(cand):
                    map.append(
                        int("".join([str(i + 1), str(j + 1)]))
                    ) if i != j else map.append(i + 1)
        map.sort()
        return map


class PartialsClueMap(ClueMapBase):
    """Clue map for the Partials clue type.

    Examples: "sum", "product".
    """

    def __init__(
        self,
        digits: List[int],
        prop_func: Callable,
        attribute: str,
        combo_size: int = 2,
    ) -> None:
        """Sets the attributes for the Partials clue map."""
        super().__init__(digits)
        self.prop_func = prop_func
        self.attribute = attribute
        self.combo_size = combo_size
        self.num_map = self.build_clue()

    def __repr__(self):
        """String representation of the instance including the attribute name"""
        return self.attribute.capitalize() + super().__repr__()

    def build_clue(self) -> List[Tuple[Tuple[int, int]]]:
        """Checks the partial combinations to see which digit combinations satisfy the
        prop_func evaluation. Generates a map for partial functions such as sum and
        product.

        Example:
            >>> self.digits = [1, 2, 2, 3, 6]
            >>> self.prop_func = is_product()
            >>> map = self.build_clue()
            >>> map
            [(), ((0, 2),), ((0, 1),), (), ((1, 3), (2, 3))]


        Args:
            prop_func: The function used to evaluate the group of digits
            attribute: Used to build the name of the formatting method
                e.g. 'partial_sums' to use the method format_partial_sums_clue()

        Returns:
            map: Numeric representation of the partial function results.

        """
        map = [[] for _ in self.digits]
        for i, val in enumerate(self.digits):
            for (j, x), (k, y) in itertools.combinations(
                enumerate(self.digits), self.combo_size
            ):
                if j != i and k != i and self.prop_func(x, y, val):
                    map[i].append((j, k))

        return [tuple(sorted(row)) for row in map]
