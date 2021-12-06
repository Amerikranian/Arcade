import pygame
import re
from .base_game import Game, GameObserver

DEFAULT_MATCH_RE = "^.+$"
EVT_UNICODE = "unicode"
EVT_TEXT_SUBMIT = "text_submit"


class TextGame(Game):
    """A class designed to simplify creation of text-based games, such as hangman"""

    def handle_input(self, delta, input_state):
        # We check for unicode first
        if input_state.keypress_event is not None:
            char = input_state.keypress_event.unicode
            if len(char) > 0:
                self.send_notification(EVT_UNICODE, char=char)

        # We also check for user wanting to submit the text
        if input_state.key_pressed(pygame.K_RETURN):
            self.send_notification(EVT_TEXT_SUBMIT)

        super().handle_input(delta, input_state)


class TextGameObserver(GameObserver):
    def __init__(self, verification_regex="", ignorecase=True):
        super().__init__()
        if len(verification_regex) == 0:
            verification_regex = DEFAULT_MATCH_RE
        if ignorecase:
            self.regex = re.compile(verification_regex, re.I)
        else:
            self.regex = re.compile(verification_regex)
        self.text = ""
        self.last_char_added = ""

    def handle_unicode(self, ctx, *args, **kwargs):
        """Called when a character is received"""
        char = kwargs["char"]
        if not re.match(self.regex, char):
            return False
        self.text += char
        # We may not necessarily want to speak what was just typed.
        # We leave that choice for the inheriting class
        self.last_char_added = char
        return True

    def handle_text_submit(self, ctx):
        """Called when the user attempts to submit text"""
        pass
