import json
from game_data_manager import GAME_KEY_QUERY, GAME_VARIATIONS_QUERY


class Player:
    """A generic class to store information about player's progress.
    Will most likely be extended as more features are added"""

    def __init__(self):
        self.game_state = {}
        self.last_played_game = ""

    def set_state(self, state):
        self.game_state = state

    def fetch_unlocked_games(self):
        return self.game_state[GAME_KEY_QUERY].keys()

    def fetch_unlocked_game_variations(self, game):
        if game not in self.game_state[GAME_KEY_QUERY]:
            raise ValueError(
                'The provided game, "%s", is not in game state list. Valid options are %s'
                % (game, ", ".join(self.fetch_unlocked_games()))
            )
        return self.game_state[GAME_KEY_QUERY][game][GAME_VARIATIONS_QUERY].keys()

    def fetch_unlocked_game_variation_difficulties(self, game, variation):
        vars = self.fetch_unlocked_game_variations(game)
        if variation not in vars:
            raise ValueError(
                'The provided variation for %s, "%s", is not in the game variation list. Valid options are %s'
                % (game, variation, ", ".join(vars))
            )
        return self.game_state[GAME_KEY_QUERY][game][GAME_VARIATIONS_QUERY][variation]

    def save(self):
        # We only have one thing to save for now
        return json.dumps(self.game_state)

    def set_last_played_game(self, g):
        self.last_played_game = g

    def fetch_last_game_played(self):
        return self.last_played_game
