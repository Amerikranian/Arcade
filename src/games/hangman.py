import cytolk.tolk as tolk
from .text_game import TextGame, TextGameObserver


class Hangman(TextGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty, HangmanObs())


class HangmanObs(TextGameObserver):
    def handle_unicode(self, ctx, *args, **kwargs):
        if not super().handle_unicode(ctx, *args, **kwargs):
            return False
        tolk.output(self.last_char_added, True)
