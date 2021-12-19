import os
from game_data_manager import GameDataManager
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

    def load_resources(self):
        """Used to load resources like word database and game information"""
        # Should probably be changed to offer a more standardize file interface
        # This way we have all file management in one spot and can possibly add a crypto backend, if we make it that far
        self.gdm.load(GAME_INFO_PATH)
        if not os.path.isfile(PLAYER_SAVE_PATH):
            data = self.gdm.generate_new_player_data()
            self.player.set_game_state(data["games"])
            self.player.set_stat_state(data["stats"])
        else:
            pass
        self.word_db.load(WORD_DB_PATH)

    def free_resources(self):
        """Intended to be used as a method of cleanup for things like sqlite and later sound system"""
        self.word_db.close()
