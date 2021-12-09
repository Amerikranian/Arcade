import cytolk.tolk as tolk
import pygame
from .text_game import TextGame, TextGameObserver

# Sent when user requests to see the entire word
EVT_WORD_CHECK = "word_check"


class Hangman(TextGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty, HangmanObs())

    def handle_input(self, delta, input_state):
        super().handle_input(delta, input_state)
        if input_state.key_pressed(pygame.K_TAB):
            self.send_notification(EVT_WORD_CHECK)


class HangmanObs(TextGameObserver):
    def __init__(self):
        super().__init__("^[a-z]$", True)
        self.remaining_guesses = 0
        self.guessed_letters = set()

    def handle_start(self, game, *args, **kwargs):
        self.text = game.context.word_db.fetch_random_word(4, 8)
        self.remaining_guesses = 10

    def handle_text_unicode(self, game, char, difficulty, *args, **kwargs):
        # We override this because Hangman handles letters differently
        if not self.is_char_matching(char):
            return False
        if char in self.guessed_letters:
            if difficulty > 0:
                self.remaining_guesses -= 1
            else:
                tolk.output("You already guessed that", True)
        else:
            self.remaining_guesses -= 1
            self.guessed_letters.add(char)
            if char in self.text:
                self.announce_word()
            else:
                tolk.output("No such luck", True)
        return True

    def handle_text_scroll(self, game, *args, **kwargs):
        if not super().handle_text_scroll(game, *args, **kwargs):
            return False
        tolk.output(self.fetch_word_character(self.text[self.cursor]))
        return True

    def handle_word_check(self, game, *args, **kwargs):
        tolk.output("".join(self.fetch_word_character(i) for i in self.text))

    def fetch_word_character(self, char):
        return "*" if char not in self.guessed_letters else char

    def announce_word(self):
        tolk.output(",".join(self.fetch_word_character(i) for i in self.text))

    def calculate_cursor_offset(self, offset, direction):
        return min(
            super().calculate_cursor_offset(self.cursor, direction), len(self.text) - 1
        )
