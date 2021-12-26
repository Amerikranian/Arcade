from json_parser.node_constants import (
    NODE_RES_EQ,
    NODE_RES_GT,
    NODE_RES_GTQ,
    NODE_RES_LT,
    NODE_RES_LTQ,
    NODE_ENFORCED_DICT,
    NODE_SINGLETYPED,
)

# Storage for default settings
DEFAULTS = "defaults"
# Game difficulty
DIFFICULTY = "difficulties"
# Game documentation
DOC = "game_docstring"
# What is shown in the main menu
GAME_DISPLAY_NAME = "display_name"
# Dictates whether the given game is unlocked by default
GAME_UNLOCKED = "unlocked_by_default"
# Game modes
GAME_VARIATIONS = "game_variations"
# Game statistics
GAME_STATS = "stat_items"
# objects with __len__ wanting to not be None or its equivalent
OBJ_WITH_LEN_ARGS = len, 1, NODE_RES_GTQ
# data game path
DATA_GAME_PATH = "games"
# Stat class types
STAT_CLS_TYPE = "cls"
# Stat output messages
STAT_OUTPUT_MSG = "output_msg"

# keys to ensure data sanity
# Top-level
REQUIRED_DATA_KEYS = DATA_GAME_PATH, DEFAULTS
# Stat keys, mostly for cosmetic purposes
REQUIRED_STAT_KEYS = STAT_CLS_TYPE, STAT_OUTPUT_MSG


GAME_GRAMMAR = {
    DIFFICULTY: (NODE_ENFORCED_DICT, int, str, *OBJ_WITH_LEN_ARGS),
    DOC: (NODE_SINGLETYPED, str, None, *OBJ_WITH_LEN_ARGS),
    GAME_UNLOCKED: (
        NODE_SINGLETYPED,
        bool,
    ),
    GAME_DISPLAY_NAME: (NODE_SINGLETYPED, str, None, *OBJ_WITH_LEN_ARGS),
    GAME_VARIATIONS: (NODE_SINGLETYPED, list, str, *OBJ_WITH_LEN_ARGS),
}

# We make GAME_GRAMMAR keys be required for defaults so it can serve as our backup setting
# We exclude `GAME_DISPLAY_NAME` because the procedure for replacing it is slightly different--it's either the class name or the provided string, and defaults won't help with either case
DEFAULT_EXCLUSIONS = (GAME_DISPLAY_NAME,)
REQUIRED_DEFAULTS_KEYS = [k for k in GAME_GRAMMAR if k not in DEFAULT_EXCLUSIONS]

STAT_GRAMMAR = NODE_ENFORCED_DICT, str, str, *OBJ_WITH_LEN_ARGS
