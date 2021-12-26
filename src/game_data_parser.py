from constants import (
    DATA_GAME_PATH,
    DEFAULTS,
    GAME_GRAMMAR,
    GAME_STATS,
    REQUIRED_DATA_KEYS,
    REQUIRED_DEFAULTS_KEYS,
    REQUIRED_STAT_KEYS,
    STAT_GRAMMAR,
)
from json_parser import JSONParser as JP


class ParserError(Exception):
    def __init__(self, name, exc):
        super().__init__("Failed to parse %s: %s" % (name, exc))


class GameDataParser:
    def __init__(self):
        self.parser = JP()
        self.parser.add_parser_node("game_grammar", GAME_GRAMMAR)
        # Due to generic nature of stats, we'll have to go through and verify things by hand
        self.stat_verification_node = self.parser.create_nodes_from_args(STAT_GRAMMAR)

    def verify_data(self, data):
        self._ensure_keys_exist("data", data, REQUIRED_DATA_KEYS)
        # Verify defaults
        self.verify_game(DEFAULTS, data[DEFAULTS], REQUIRED_DEFAULTS_KEYS)
        # It's okay if stats are empty
        # It just means that each game will need to define its own stat list if it wants to to store anything
        self.verify_stats(
            f"{DEFAULTS}/{GAME_STATS}",
            data[DEFAULTS].get(GAME_STATS, {}),
            REQUIRED_STAT_KEYS,
        )
        games = data[DATA_GAME_PATH]
        for k, v in games.items():
            # The parser works on principle of ignoring any ambiguous text
            # In theory, it's smart enough to recognize the beginnings of the wrong text and won't bother investigating false paths
            # As such, we just toss possibly false data at it--its job is to ensure that if correct data exists it will be of the promised type(s)
            # We also don't give any required keys, as any missing info will be filled by game data manager
            self.verify_game(k, v)
            # Manual check for statistics as they are generic
            if GAME_STATS in v:
                self.verify_stats(k, v[GAME_STATS], REQUIRED_STAT_KEYS)

    def verify_game(self, game_name, game, required_keys=None):
        try:
            self.parser.parse("game_grammar", game)
        except (TypeError, ValueError) as e:
            raise ParserError(game_name, e)
        if required_keys is not None:
            self._ensure_keys_exist(game_name, game, required_keys)

    def verify_stats(self, game_name, stats, required_keys=None):
        for k, v in stats.items():
            try:
                self.stat_verification_node.visit(v)
            except (TypeError, ValueError) as e:
                raise ParserError(f"{game_name}/{k}", e)
            # Verify `required_keys` now because anything above this level is unpredictable
            if required_keys is not None:
                self._ensure_keys_exist(game_name, v, REQUIRED_STAT_KEYS)

    def _ensure_keys_exist(self, name, data, keys):
        for k in keys:
            if k not in data:
                raise ParserError(
                    f"{name}/{k}", KeyError("The provided key, %s, does not exist" % k)
                )
