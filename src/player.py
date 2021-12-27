import json
from constants import GAME_VARIATIONS


class Player:
    """A generic class to store information about player's progress.
    Will most likely be extended as more features are added"""

    def __init__(self):
        self.game_state = {}
        self.statistics = {}
        self.last_played_game = ""

    def set_game_state(self, state):
        self.game_state = state

    def set_stat_state(self, state):
        self.statistics = state

    def fetch_unlocked_games(self):
        return list(self.game_state)

    def fetch_unlocked_game_variations(self, game):
        if game not in self.game_state:
            raise ValueError(
                'The provided game, "%s", is not in game state list. Valid options are %s'
                % (game, ", ".join(self.fetch_unlocked_games()))
            )
        return list(self.game_state[game][GAME_VARIATIONS])

    def fetch_unlocked_game_variation_difficulties(self, game, variation):
        vars = self.fetch_unlocked_game_variations(game)
        if variation not in vars:
            raise ValueError(
                'The provided variation for %s, "%s", is not in the game variation list. Valid options are %s'
                % (game, variation, ", ".join(vars))
            )
        return self.game_state[game][GAME_VARIATIONS][variation]

    def _assemble_recursive_stat_dict(self, initial_dict):
        dct = {}
        for k in initial_dict:
            if isinstance(initial_dict[k], dict):
                dct[k] = self._assemble_recursive_stat_dict(initial_dict[k])
            else:
                dct[k] = initial_dict[k].to_json()
        return dct

    def to_json(self):
        return {
            "games": self.game_state,
            "stats": self._assemble_recursive_stat_dict(self.statistics),
        }

    def set_last_played_game(self, g):
        self.last_played_game = g

    def fetch_last_game_played(self):
        return self.last_played_game

    def fetch_unlocked_game_stats(self, game, variation, difficulty):
        if game not in self.statistics:
            raise ValueError(
                'The statistics for the requested game, "%s", do not exist' % game
            )
        return self.statistics[game][GAME_VARIATIONS][variation][difficulty]
