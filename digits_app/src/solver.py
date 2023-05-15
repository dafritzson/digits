"""Clue solver application for reducing the set of clues needed to solve a number."""
from itertools import combinations
from random import randint
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import digits_app.src.clues.clue as c
import digits_app.src.clues.clue_map as cm
from digits_app.src.constants import CLUE_TYPE_MAP, CLUES, NEGATIVE_CONSTRAINT_CLUES
from digits_app.src.utility_methods import (
    default_map_to_key,
    digits_to_num,
    snake_to_camelcase,
    timed,
)


class Solver:
    """Finds the smallest set of clues to provide the user for the given number that
    guarantees there is only one answer.
    """

    def __init__(
        self,
        digits: List[int],
        maps: Dict[Type[cm.ClueMapBase], List],
        clues: Dict[str, List[Type[c.Clue]]],
        difficulty: str,
        map_files: Dict,
    ) -> None:
        """The set of clues generated are based on the difficulty and the provided
        numeric maps for each clue type.

        Args:
            digits: List of digits of the answer.
            maps: Numeric maps generated for the answer from the `ClueGenerator`.
            clues: All clues generated for the answer from the `ClueGenerator`.
            difficulty: Level of difficulty to determine which clues to give the user.
            map_files: Loaded map file objects.
        """
        self.digits = digits
        self.answer = digits_to_num(digits)
        self.maps = maps
        self.difficulty = difficulty
        self.map_files = map_files
        self.clues = clues
        self.final_clues = None
        matches = self.get_all_matches()
        matches = self._filter_by_length(matches)
        solved_combos = self.find_overlaps(matches)
        if solved_combos:
            self.final_clues, self.num_clue_types = self.find_most_fun_clues(
                solved_combos
            )
            self.add_negative_constraint_clues()
            self.update_final_clue_keys()
        else:
            print("Unable to provide enough clues for you to guess the number.")
            print(f"Answer was {self.answer}. Try another number.")

    def _filter_by_length(self, matches: Dict[str, List[int]]) -> Dict[str, List[int]]:
        for attr, _matches in matches.items():
            matches[attr] = list(
                filter(lambda match: len(str(match)) == len(str(self.answer)), _matches)
            )
        return matches

    @staticmethod
    def format_clue_type(clue_type: str) -> str:
        rename_map = {"multiples": "divided"}
        renamed_type = rename_map.get(clue_type)
        new_key = renamed_type or clue_type
        return new_key.upper().replace("_", " ")

    def add_negative_constraint_clues(self) -> None:
        for clue_type in self.final_clues:
            negative_clue = NEGATIVE_CONSTRAINT_CLUES.get(clue_type)
            limit_msg = None
            if negative_clue:
                parent_clue_type = CLUE_TYPE_MAP.get(clue_type)
                clue_type_config = (
                    CLUES[parent_clue_type][clue_type]
                    if parent_clue_type
                    else CLUES[clue_type][clue_type]
                )
                if clue_type_config:
                    limit_msg = self._format_limit_msg(clue_type_config)
                formatted_clue = negative_clue.format(
                    key=self.format_clue_type(clue_type), limit_msg=limit_msg
                )
                self.final_clues[clue_type].append(formatted_clue)

    def _format_limit_msg(
        self, clue_type_config: List[Dict[str, Any]]
    ) -> Optional[str]:
        limits = None
        difficulty_limit = None
        limit_msg = ""
        if clue_type_config:
            limits: Dict[str, Dict[str, int]] = clue_type_config.get("limits")
        if limits:
            difficulty_limit = limits[self.difficulty].get("length", None)
            if not difficulty_limit:
                return ""
            limit_msg = (
                f"1 or {difficulty_limit} digit "
                if difficulty_limit > 1
                else f"1-digit "
            )
        return limit_msg

    def update_final_clue_keys(self) -> None:
        new_final_clues = {}
        for clue_type, clues in self.final_clues.items():
            new_final_clues[self.format_clue_type(clue_type)] = clues
        self.final_clues = new_final_clues

    @staticmethod
    @timed
    def find_most_fun_clues(
        solved_combos: Dict[Tuple, Dict[str, Union[List, int]]],
        combo_filter: str = "min",
        num_clues_filter: str = "min",
    ) -> Tuple[List[str], int]:
        """Filters clues by min type of clue and/or min number of clues across all clue
        combinations."""
        combo_func = min if combo_filter == "min" else max
        clues_func = min if num_clues_filter == "min" else max

        # Determine min/max size/variety of clue types from all solved combinations
        combo_size = combo_func([len(combo) for combo in solved_combos])

        # Determine min/max number of clues from all solved combinations
        clue_size = clues_func([info["num_clues"] for info in solved_combos.values()])

        # Pull the min/max combos based only on the min/max combination size
        combos = dict(
            filter(lambda item: len(item[0]) == combo_size, solved_combos.items())
        )

        # Pull the min/max combos based only on the min/max number of clues
        # (Not typically used since the combos should probably be filtered by combo size first)
        clues = dict(
            filter(
                lambda item: item[1]["num_clues"] == clue_size,
                solved_combos.items(),
            )
        )

        # Determine min/max number of clues for each min/max combination size
        num_clues = clues_func([info["num_clues"] for info in combos.values()])

        # Pull the combos with the min/max number of clues from the min/max combos
        funnest_combos = dict(
            filter(
                lambda item: item[1]["num_clues"] == num_clues,
                combos.items(),
            )
        )
        clue_num = randint(0, len(funnest_combos.keys()) - 1)
        return list(funnest_combos.items())[clue_num][1]["clues"], combo_size

    @timed
    def find_overlaps(
        self, all_matches: Dict[str, List[int]]
    ) -> Dict[Tuple, Dict[str, Union[List, int]]]:
        """Reduces the matching numbers for each clue down to solved combinations of
        clues.

        Solved combinations mean there is only one number that is shared across all clue
        types in that combination. Therefore the clues presented to the user can only
        have one solution.

        Args:
            all_matches: Lists of matching numbers keyed by clue type.

        Returns:
            solved_combos: Matching clues and number of clues keyed by each combination
                of clue types.
        """
        solved_combos = {}
        solved = False
        clue_types = (  # Provide max number of clue types if in easy mode
            range(len(all_matches), 0, -1)
            if self.difficulty == "easy"
            else range(1, len(all_matches) + 1)
        )
        for size in clue_types:
            # size represents a combination size of several clue types
            # e.g. If the combination is ["prime", "product", "even"] then size == 3
            for combo in map(dict, combinations(all_matches.items(), size)):
                # combo is a dict keyed by clue type/attribute, values are lists of matching numbers
                # that share clue maps for each clue type.
                # e.g. combo = {"prime": [1234, 5678], "product": [1234, 2468], "even": [1234, 3456]}
                overlapping_nums = set.intersection(*map(set, combo.values()))
                if len(overlapping_nums) == 1:
                    combo_clues = dict(
                        filter(lambda item: item[0] in combo, self.clues.items())
                    )
                    num_clues = sum([len(clues) for clues in combo_clues.values()])
                    solved_combos[tuple(combo.keys())] = {
                        "clues": combo_clues,
                        "num_clues": num_clues,
                    }
                    solved = True
                    # print(f"Solved combo: {list(combo.keys())}. Num clues: {num_clues}")
            if solved:
                break
        return solved_combos

    def get_all_matches(
        self, clues: Dict[str, Dict[str, Dict[str, Any]]] = CLUES
    ) -> Dict[str, List[int]]:
        """Creates a map of numbers that have matching numeric maps with the answer's
        maps for all clue types.

        Args:
            clues: All clues and their accompanying configuration parameters.

        Returns:
            matches: Mapping of clues to their corresponding matches.
        """
        matches = {}
        for clue, _kwargs in clues.items():
            func_name = f"get_{clue}_matches"
            for kwargs in _kwargs.values():
                key = kwargs.get("attribute") or clue
                map_file = self.map_files[self.difficulty][key]
                try:
                    c_matches = getattr(self, func_name)(
                        map_file=map_file, clue=clue, **kwargs
                    )
                except AttributeError:
                    print(
                        f"Function {func_name} not found. Continuing with other clues."
                    )
                    continue
                if isinstance(c_matches, list):
                    matches[clue] = c_matches
                elif isinstance(c_matches, dict):
                    matches.update({attr: _mts for attr, _mts in c_matches.items()})
        return matches

    def get_simple_matches(
        self,
        all_maps: Dict,
        clue: str,
        map_key_func: Callable = default_map_to_key,
    ) -> List[int]:
        """Creates a map of numbers that have matching numeric maps with the answer's
        maps for simple clue types.

        Simple clue types are those that don't have a higher-level abstracted clue type.
        These clue types don't have subset dicts/kwargs that need to be parsed.
        Examples of a simple clue type are "multiples" or "order".

        Args:
            all_maps: All numeric maps for a given clue type. Loaded from the map file.
            clue: Clue type.
            map_key_func: Converts the numeric map to a key-able form so it can be
                accessed from the map file.

        Returns:
            matches: Numbers with matching numeric maps for the given clue type, keyed
                by the clue type.
        """
        matches = []
        cm_name = snake_to_camelcase(clue) + "ClueMap"
        num_map = self.maps.get(cm_name)
        try:
            num_map = map_key_func(num_map)
        except TypeError:
            print(
                f"Unable to cast the following num_map using {map_key_func.__name__}: "
                f"{num_map}"
            )
            return []
        try:
            matches = all_maps.get(
                num_map, []
            )  # TODO: Why does this error only on deployment?
        except KeyError:
            print(f"KeyError for {num_map}. All keys: {list(all_maps.keys())}")
        return matches

    def get_variety_matches(
        self,
        all_maps: Dict,
        clue: str,
        attribute: str,
        map_key_func: Callable = default_map_to_key,
    ) -> Dict[str, List[int]]:
        """Creates a map of numbers that have matching numeric maps with the answer's
        maps for variety clue types.

        Variety clue types have a higher-level abstracted clue type. These clue types
        have subset dicts/kwargs that need to be parsed to specify the lower-level clue
        type.
        Examples of a variety clue type are "special_properties" or "partials" where the
        lower-level clue types would be "prime" and "fibonacci" or "sum" and "product",
        respectively.

        Args:
            all_maps: All numeric maps for a given clue type. Loaded from the map file.
            clue: Clue type.
            attribute: Lower-level clue type. (e.g. "prime" or "fibonacci").
            map_key_func: Converts the numeric map to a key-able form so it can be
                accessed from the map file.

        Returns:
            matches: Numbers with matching numeric maps for the given clue type, keyed
                by the attribute rather than the higher-level clue type.
        """
        cm_base = snake_to_camelcase(clue) + "ClueMap"
        matches = {}
        cm_name = snake_to_camelcase(attribute) + cm_base
        answer_map = self.maps.get(cm_name)
        answer_map = map_key_func(answer_map)
        matching_nums = all_maps[attribute][answer_map]
        matches[attribute] = matching_nums
        return matches

    @timed
    def get_multiples_matches(
        self, map_file: Dict, clue: str = "multiples", **kwargs
    ) -> List[int]:
        """Gets matches of numeric maps for multiples clues"""

        def _map_to_key(num_map: List):
            return tuple(map(tuple, num_map))

        return self.get_simple_matches(map_file, clue, _map_to_key)

    @timed
    def get_total_sum_matches(
        self, map_file: Dict, clue: str = "total_sum"
    ) -> List[int]:
        """Gets matches of numeric maps for total sum clues"""

        return self.get_simple_matches(map_file, clue)

    @timed
    def get_even_matches(self, map_file: Dict, clue: str = "even") -> List[int]:
        """Gets matches of numeric maps for even clues"""
        matches = []
        cm_name = snake_to_camelcase(clue) + "ClueMap"
        num_map = self.maps.get(cm_name)
        matching_maps = {
            candidate_map: map_file[candidate_map]
            for candidate_map in map_file
            if candidate_map.count(1) == num_map.count(1)
        }
        num_map = default_map_to_key(num_map)
        for map in matching_maps:
            matches.extend(map_file[map])
        return matches

    @timed
    def get_order_matches(self, map_file: Dict, clue: str = "even") -> List[int]:
        """Gets matches of numeric maps for order clues"""
        return self.get_simple_matches(map_file, clue)

    @timed
    def get_special_properties_matches(
        self, map_file: Dict, clue: str = "special_properties", **kwargs
    ) -> Dict[str, List[int]]:
        """Gets matches of numeric maps for special properties clues"""
        return self.get_variety_matches(
            map_file, clue, attribute=kwargs.get("attribute")
        )

    @timed
    def get_partials_matches(
        self, map_file: Dict, clue: str = "partials", **kwargs
    ) -> Dict[str, List[int]]:
        """Gets matches of numeric maps for partials clues"""
        return self.get_variety_matches(
            map_file, clue, attribute=kwargs.get("attribute")
        )
