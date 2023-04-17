"""Classes for each individual clue type."""
from abc import abstractmethod
from typing import List

from digits_app.src.constants import INDEX_STRING_MAP
from digits_app.src.utility_methods import bold


class Clue:
    def __init__(self, digits: List[str]) -> None:
        self.digits = digits

    def __str__(self) -> str:
        return self.format_for_display()

    @abstractmethod
    def format_for_display(self):
        """Overwrite in child classes"""


class OrderClue(Clue):
    def __init__(self, digits: List[str], ascending: bool, descending: bool) -> None:
        super().__init__(digits)
        self.ascending = ascending
        self.descending = descending
        self.keyword = bold("order")

    def format_for_display(self) -> str:
        """Formats the order of digits clue"""
        base = "My digits are in {} {}"
        if self.ascending:
            return base.format("ascending", self.keyword)
        elif self.descending:
            return base.format("descending", self.keyword)
        else:
            return f"My digits are in neither ascending nor descending {self.keyword}"


class TotalSumClue(Clue):
    def __init__(self, digits: List[str], digit: int, comparison: str) -> None:
        super().__init__(digits)
        self.digit = digit
        self.comparison = comparison
        self.keyword = bold("total sum")

    def format_for_display(self):
        """Formats the sum clue"""
        base = "My {} digit is {} the {} of all my other digits"
        s_idx = INDEX_STRING_MAP[self.digit]
        return base.format(s_idx, self.comparison, self.keyword)


class EvenClue(Clue):
    def __init__(self, digits: List[str], num_even: int) -> None:
        super().__init__(digits)
        self.num_even = num_even
        self.keyword = bold("even")

    def format_for_display(self) -> str:
        """Formats the even or odd clue"""
        num_even = str(self.num_even) if self.num_even > 0 else "None"
        return f"{num_even} of my digits are {self.keyword}"


class MultipleClue(Clue):
    def __init__(
        self,
        digits: List[str],
        factor: int,
        multiple: int,
        multiplier: int,
    ) -> None:
        super().__init__(digits)
        self.keyword = bold("divided")
        self.factor = factor
        self.multiple = multiple
        self.multiplier = multiplier
        self.s_idx1 = INDEX_STRING_MAP[self.factor]
        self.s_idx2 = INDEX_STRING_MAP[self.multiple]
        self.bases = [
            (
                "My {} digit {} by {} equals my {} digit",
                [self.s_idx2, self.keyword, self.multiplier, self.s_idx1],
            ),
            (
                "My {} digit {} by my {} digit equals 1",
                [self.s_idx1, self.keyword, self.s_idx2],
            ),
            (
                "My {} digit is the same as my {} digit",
                [self.s_idx1, self.s_idx2],
            ),
        ]

    def format_for_display(self):
        """Formats the multiples clue"""
        if self.multiplier == -1:  # zero divided by zero case
            base = self.bases[2]
        elif self.multiplier == 1:  # same number for both digits, but not zeros
            base = self.bases[1]
        else:  # different numbers, multiples of each other
            base = self.bases[0]

        return base[0].format(*base[1])


class SpecialPropertiesClue(Clue):
    def __init__(self, digits: List[str], attribute: str, special_digs: int) -> None:
        super().__init__(digits)
        s_digs = str(special_digs)
        self.first = s_digs[0]
        self.second = None if len(s_digs) == 1 else s_digs[1]
        self.keyword = bold(attribute)

    def format_for_display(self):
        s_idx1 = INDEX_STRING_MAP[int(self.first) - 1]
        s_idx2 = None if not self.second else INDEX_STRING_MAP[int(self.second) - 1]
        if not s_idx2:
            return f"My {s_idx1} digit is a {self.keyword} number"
        return (
            f"Joining my {s_idx1} through {s_idx2} digits makes a {self.keyword} number"
        )


class PartialsClue(Clue):
    def __init__(
        self,
        digits: List[str],
        target_idx: int,
        f1_idx: int,
        f2_idx: int,
        partial_type: str,
    ) -> None:
        super().__init__(digits)
        self.t_idx = target_idx
        self.f1_idx = f1_idx
        self.f2_idx = f2_idx
        self.keyword = bold(partial_type)

    def format_for_display(self):
        """Formats the partial clues"""
        st_idx = INDEX_STRING_MAP.get(self.t_idx, None)
        s_idx1 = INDEX_STRING_MAP.get(self.f1_idx, None)
        s_idx2 = INDEX_STRING_MAP.get(self.f2_idx, None)
        if all([st_idx, s_idx1, s_idx2]):
            return f"My {st_idx} digit is the {self.keyword} of my {s_idx1} and {s_idx2} digits"
        return f"None of my digits are the {self.keyword} of a combination of my other digits."
