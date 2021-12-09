import pygame
import re
from .base_game import Game, GameObserver

DEFAULT_MATCH_RE = "^.+$"
EVT_UNICODE = "text_unicode"
EVT_TEXT_SUBMIT = "text_submit"
EVT_SCROLL = "text_scroll"


class TextGame(Game):
    """A class designed to simplify creation of text-based games, such as hangman"""

    def handle_input(self, delta, input_state):
        # We check for unicode first
        if input_state.keypress_event is not None:
            char = input_state.keypress_event.unicode
            if len(char) > 0:
                self.send_notification(EVT_UNICODE, char=char)

        # Handle scrolling stuff
        if input_state.key_pressed(pygame.K_LEFT):
            self.send_notification(EVT_SCROLL, direction=-1)
        elif input_state.key_pressed(pygame.K_RIGHT):
            self.send_notification(EVT_SCROLL, direction=1)

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
        self.cursor = 0
        self.last_char_added = ""

    def handle_text_unicode(self, game, *args, **kwargs):
        """Called when a character is received"""
        char = kwargs["char"]
        if not self.is_char_matching(char):
            return False
        self.text = self.text[: self.cursor] + char + self.text[self.cursor :]
        self.cursor += len(char)
        # We may not necessarily want to speak what was just typed.
        # We leave that choice for the inheriting class
        self.last_char_added = char
        return True

    def is_char_matching(self, char):
        return re.match(self.regex, char)

    def calculate_cursor_offset(self, offset, dir):
        return max(0, min(len(self.text), offset + dir))

    def handle_text_scroll(self, game, *args, **kwargs):
        # We add the absolute basic support for moving through text, as a lot of games handle this slightly differently
        crc = self.calculate_cursor_offset(self.cursor, kwargs["direction"])
        if crc != self.cursor:
            self.cursor = crc
            return True
        return False
