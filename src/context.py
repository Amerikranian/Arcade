import json
import os
from copy import deepcopy
from game_data_manager import GAME_VARIATIONS_QUERY, GameDataManager
from player import Player
from word_db import WordDB

GAME_INFO_PATH = "data/games/info.json"
PLAYER_SAVE_PATH = "data/save.json"
WORD_DB_PATH = "data/games/word_list.db"


class Context:
    """A class mainly used as an injection method.
    Anything that states need to access on a persistent basis, such as a sound system, should probably go here"""

    def __init__(self):
        self.gdm = GameDataManager()
        self.player = Player()
        self.word_db = WordDB()

    def _dispatch_attrs_to_stats(self, arg_dict, stat_dict):
        """Upon load, recreate the objects in the save file"""
        dct = {}
        for arg, res in arg_dict.items():
            # Case 1: the argument exists in both dictionaries
            if arg in stat_dict:
                # We copy the object and assign new attributes
                stat_obj = deepcopy(stat_dict[arg])
                stat_obj.from_json(res)
                dct[arg] = stat_obj
            # Case 2: res is a dict
            elif isinstance(res, dict):
                dct[arg] = self._dispatch_attrs_to_stats(res, stat_dict)
            # Case 3: res is literally anything else
            else:
                raise ValueError(
                    "Failed to match %s as it does not exist within %s"
                    % (arg, ", ".join(stat_dict.keys()))
                )

        return dct

    def load_resources(self):
        """Used to load resources like word database and game information"""
        # Should probably be changed to offer a more standardize file interface
        # This way we have all file management in one spot and can possibly add a crypto backend, if we make it that far
        self.gdm.load(GAME_INFO_PATH)
        data = {}
        if not os.path.isfile(PLAYER_SAVE_PATH):
            data = self.gdm.generate_new_player_data()
        else:
            with open(PLAYER_SAVE_PATH, "r") as f:
                temp_data = json.load(f)
            data["games"] = temp_data.pop("games")
            data["stats"] = {}
            for game in data["games"]:
                data["stats"][game] = self._dispatch_attrs_to_stats(
                    temp_data["stats"][game],
                    self.gdm.gather_unlocked_game_diff_stats(self.gdm.fetch_game(game)),
                )

        self.player.set_game_state(data["games"])
        self.player.set_stat_state(data["stats"])
        self.word_db.load(WORD_DB_PATH)

    def export_resources(self):
        """Anything related to saving should go here"""
        data = self.player.to_json()
        with open(PLAYER_SAVE_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def free_resources(self):
        """Intended to be used as a method of cleanup for things like sqlite and later sound system"""
        self.word_db.close()
