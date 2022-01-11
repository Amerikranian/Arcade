import synthizer

from audio import BufferCache, SoundManager
from constants import DATA_GAME_PATH, DEFAULTS
from game_data_manager import GameDataManager
from game_data_parser import GameDataParser
from player import Player
from speech_manager import SpeechManager
from word_db import WordDB

GAME_INFO_PATH = "data/games/info.json"
PLAYER_SAVE_PATH = "data/save.json"
WORD_DB_PATH = "data/games/word_list.db"


class Context:
    """A class mainly used as an injection method.
    Anything that states need to access on a persistent basis, such as a sound system, should probably go here"""

    def __init__(self, file_mgr, snd_mgr):
        self.file_manager = file_mgr
        self.gdm = GameDataManager()
        self.player = Player()
        self.spm = SpeechManager()
        self.word_db = WordDB()
        self.sounds = snd_mgr

    def _dispatch_attrs_to_stats(self, arg_dict, stat_dict):
        """Upon load, recreate the objects in the save file"""
        dct = {}
        for arg, res in arg_dict.items():
            # Case 1: the argument exists in both dictionaries
            if arg in stat_dict:
                # We copy the object and assign new attributes
                stat_obj = stat_dict[arg]()
                stat_obj.from_json(res)
                dct[arg] = stat_obj
            # Case 2: res is a dict
            elif isinstance(res, dict):
                dct[arg] = self._dispatch_attrs_to_stats(res, stat_dict)
            # Case 3: res is anything else
            else:
                raise ValueError(
                    "Failed to match %s as it does not exist within %s"
                    % (arg, ", ".join(stat_dict))
                )

        return dct

    def load_resources(self):
        """Used to load resources like word database and game information"""
        # Load db
        self.word_db.load(WORD_DB_PATH)
        initial_data = self.file_manager.fetch_json(GAME_INFO_PATH)
        # Data integrity check
        # We only parse data once
        # The availability of a parser may be changed in the future if we find that it is constantly being used
        # As of now, though, it stays local
        parser = GameDataParser()
        parser.verify_data(initial_data)

        # `initial_data` is guaranteed to have `DATA_GAME_PATH` and `DEFAULTS` due to parser constraint
        self.gdm.set_default_settings(initial_data[DEFAULTS])
        self.gdm.set_games(initial_data[DATA_GAME_PATH])

        data = {}
        stats = {}
        if not self.file_manager.file_exists(PLAYER_SAVE_PATH):
            data, stats = self.gdm.generate_new_player_data()
        else:
            temp_data = self.file_manager.fetch_json(PLAYER_SAVE_PATH)
            data = temp_data.pop("games")
            stats = {}
            for game in data:
                stats[game] = self._dispatch_attrs_to_stats(
                    temp_data["stats"][game],
                    self.gdm.gather_unlocked_game_stats(game, False),
                )

            # Update player data with any new unlocked by default games
            new_game_data, new_game_statistics = self.gdm.gather_unlocked_games(
                list(data)
            )
            data.update(new_game_data)
            stats.update(new_game_statistics)

        self.player.set_game_state(data)
        self.player.set_stat_state(stats)

    def export_resources(self):
        """Anything related to saving should go here"""
        data = self.player.to_json()
        self.file_manager.write_json(data, PLAYER_SAVE_PATH)

    def free_resources(self):
        """Intended to be used as a method of cleanup for things like sqlite and later sound system"""
        self.word_db.close()
