from os.path import join
from constants import DEFAULT_SOUND_DIR, DEFAULT_SOUND_EXT
from screen import Screen


class Game(Screen):
    """The basic idea is to inherit this class and override any method from the Screen class. Following this, import this in __init__.py, fix any issues, and repeat for subsequent creations.
    Each game may have a list of variations, and each variation may have its own number of difficulty modes, as described by the info.json file located within the data/games/.
    Each variation is expected to be a string, such as "Partial Anagrams", and the difficulties are expected to be integers with no specific constraints. Note that for the purposes of handling variations in code, if the variation contains spaces, they will be replaced by underscores (_)
    Variations and difficulties will be converted to their string equivalents, as either supplied by the creator or inferred by the program in the latter's case
    If not specified otherwise, each variation will have 3 default difficulties.
    """

    def __init__(self, variation, difficulty):
        super().__init__()
        self.variation = variation
        self.difficulty = difficulty

    def play(self, path, **kwargs):
        if ext is None:
            ext = DEFAULT_SOUND_EXT
        return self.context.sounds.play(join(DEFAULT_SOUND_DIR, path + ext), **kwargs)

    def play_from_dir(self, path, ext=None, **kwargs):
        if ext is None:
            ext = DEFAULT_SOUND_EXT
        return self.context.sounds.play(
            join(
                DEFAULT_SOUND_DIR,
                self.context.player.fetch_last_game_played(),
                path + ext,
            ),
            **kwargs
        )

    def stream(self, path, **kwargs):
        if ext is None:
            ext = DEFAULT_SOUND_EXT
        return self.context.sounds.stream(join(DEFAULT_SOUND_DIR, path + ext), **kwargs)

    def stream_from_dir(self, path, ext=None, **kwargs):
        if ext is None:
            ext = DEFAULT_SOUND_EXT
        return self.context.sounds.stream(
            join(
                DEFAULT_SOUND_DIR,
                self.context.player.fetch_last_game_played(),
                path + ext,
            ),
            **kwargs
        )
