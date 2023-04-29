"""Map file database builder tools."""
import os
import pickle
from typing import Any, Callable, Dict, List

import digits_app.src.clues.clue_map as cm
from digits_app.src.constants import CLUES, MAPS_DB
from digits_app.src.utility_methods import (
    default_map_to_key,
    num_to_digits,
    snake_to_camelcase,
    timed,
)


class MapsDatabaseBuilder:
    """Builds a database of pkl files representing the numeric maps of every number
    within a provided range
    """

    def __init__(self, min: int, max: int, difficulty: str) -> None:
        """Initializes the database builder for a provided range

        Args:
            min: Minimum number for which to evaluate maps
            max: Max number for which to evaluate maps
            difficulty: Clue difficulty
        """
        self.min = min
        self.max = max
        self.difficulty = difficulty
        self.paths = self.get_maps_paths(CLUES, self.difficulty)
        self.store_all_maps(CLUES)

    @staticmethod
    def get_maps_paths(
        clues: Dict[str, Dict[str, Dict[str, Any]]], difficulty: str
    ) -> Dict[str, str]:
        paths = {}
        for clue, _kwargs in clues.items():
            for kwargs in _kwargs.values():
                key = kwargs.get("attribute") or clue
                paths[key] = os.path.join(MAPS_DB, f"{difficulty}_{key}_maps.pkl")
        return paths

    def store_all_maps(self, clues: Dict[str, Dict[str, Dict[str, Any]]]):
        for clue, _kwargs in clues.items():
            func_name = f"store_{clue}_maps"
            for kwargs in _kwargs.values():
                key = kwargs.get("attribute") or clue
                try:
                    getattr(self, func_name)(path=self.paths[key], clue=clue, **kwargs)
                except AttributeError:
                    print(
                        f"Function {func_name} not found. Continuing with other clues."
                    )
                    continue

    @staticmethod
    def get_class(module: Callable, clue: str, base: str):
        try:
            clue_name = snake_to_camelcase(clue)
            map_class = getattr(module, clue_name + base)
            return map_class
        except AttributeError:
            print(f"Class {clue_name} could not be found. Skipping {clue}.")
            return None

    def store_simple_maps(
        self,
        max: int,
        path: str,
        clue: str,
        map_key_func: Callable = default_map_to_key,
        **kwargs,
    ) -> None:
        print(f"Storing all {clue} maps...")
        map_class = self.get_class(cm, clue, base="ClueMap")
        if not map_class:
            return
        maps = {}
        for val in range(1, max + 1):
            digits = num_to_digits(val)
            num_map = map_key_func(map_class(digits, **kwargs).num_map)
            maps.setdefault(num_map, [])
            maps[num_map].append(val)
        with open(path, "wb") as file:
            pickle.dump(maps, file)
        print(f"Saved {len(maps)} {clue} maps to disk.")

    def store_variety_maps(
        self,
        max: int,
        path: str,
        clue: str,
        prop_func: Callable,
        attribute: str,
        map_key_func: Callable = default_map_to_key,
        **kwargs,
    ):
        print(f"Storing all {attribute} maps...")
        map_class = self.get_class(cm, clue, base="ClueMap")
        if not map_class:
            return
        maps = {}
        maps.setdefault(attribute, {})
        for val in range(1, max + 1):
            digits = num_to_digits(val)
            map = map_key_func(
                map_class(
                    digits,
                    prop_func=prop_func,
                    attribute=attribute,
                    **kwargs,
                ).num_map
            )
            maps[attribute].setdefault(map, [])
            maps[attribute][map].append(val)
        print(f"Found {len(maps[attribute].keys())} unique maps for {attribute}")
        with open(path, "wb") as file:
            pickle.dump(maps, file)
        print(f"Saved {attribute} maps to disk.")

    @timed
    def store_multiples_maps(
        self,
        path: str,
        clue: str = "multiples",
        limits: Dict[str, Dict[str, int]] = None,
    ):
        def _map_to_key(num_map: List):
            return tuple(map(tuple, num_map))

        limit = None if not limits else limits[self.difficulty].get("length")
        self.store_simple_maps(self.max, path, clue, _map_to_key, limit=limit)

    @timed
    def store_total_sum_maps(self, path: str, clue: str = "total_sum"):
        self.store_simple_maps(self.max, path, clue)

    @timed
    def store_even_maps(self, path: str, clue: str):
        self.store_simple_maps(self.max, path, clue)

    @timed
    def store_order_maps(self, path: str, clue: str):
        self.store_simple_maps(self.max, path, clue)

    @timed
    def store_special_properties_maps(
        self, path: str, clue: str = "special_properties", **kwargs
    ):
        limit = kwargs.get("limits").get(self.difficulty).get("length")
        prop_func = kwargs.get("prop_func")
        attribute = kwargs.get("attribute")
        self.store_variety_maps(
            max=self.max,
            path=path,
            clue=clue,
            prop_func=prop_func,
            attribute=attribute,
            limit=limit,
        )

    @timed
    def store_partials_maps(self, path: str, clue: str = "partials", **kwargs):
        prop_func = kwargs.get("prop_func")
        attribute = kwargs.get("attribute")
        self.store_variety_maps(
            max=self.max,
            path=path,
            clue=clue,
            prop_func=prop_func,
            attribute=attribute,
        )
