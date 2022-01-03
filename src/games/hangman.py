import cytolk.tolk as tolk
import pygame
from .text_game import TextGame, TextGameObserver

# Sent when user requests to see the entire word
EVT_WORD_CHECK = "word_check"
# Sent when user requests to see remaining guesses
EVT_GUESS_CHECK = "guess_check"


class Hangman(TextGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(HangmanObs())

    def handle_input(self, delta, input_state):
        super().handle_input(delta, input_state)
        if input_state.key_pressed(pygame.K_TAB):
            self.send_notification(EVT_WORD_CHECK)
        elif input_state.key_pressed(pygame.K_SPACE):
            self.send_notification(EVT_GUESS_CHECK)


class HangmanObs(TextGameObserver):
    def __init__(self):
        super().__init__("^[a-z]$", True)
        self.remaining_guesses = 0
        self.guessed_letters = set()

    def handle_start(self, game, *args, **kwargs):
        self.text = game.context.word_db.fetch_random_word(4, 8)
        self.remaining_guesses = 10
        return True

    def handle_text_unicode(self, game, char, difficulty, *args, **kwargs):
        # We override this because Hangman handles letters differently
        if not self.is_char_matching(char):
            return False
        # We forgive letter repetitions on easy
        if char in self.guessed_letters and difficulty == 0:
            tolk.output("You already guessed that!")
            return True
        self.guessed_letters.add(char)
        if char not in self.text:
            self.remaining_guesses -= 1
            tolk.output("No such luck.", True)
        else:
            self.announce_word()
        return True

    def handle_text_scroll(self, game, *args, **kwargs):
        if not super().handle_text_scroll(game, *args, **kwargs):
            return False
        tolk.output(self.fetch_word_character(self.text[self.cursor]))
        return True

    def handle_word_check(self, game, *args, **kwargs):
        tolk.output("".join(self.fetch_word_character(i) for i in self.text))
        return True

    def handle_guess_check(self, game, *args, **kwargs):
        tolk.output(
            f"{self.remaining_guesses} guess{'es' if self.remaining_guesses > 1 else ''} remaining"
        )

    def fetch_word_character(self, char):
        return "*" if char not in self.guessed_letters else char

    def announce_word(self):
        tolk.output(",".join(self.fetch_word_character(i) for i in self.text))

    def calculate_cursor_offset(self, offset, direction):
        return min(
            super().calculate_cursor_offset(self.cursor, direction), len(self.text) - 1
        )

    def has_won(self):
        return all(l in self.guessed_letters for l in self.text)

    def has_lost(self):
        return self.remaining_guesses == 0

    def gather_statistics(self):
        base_stats = super().gather_statistics()
        base_stats["Hidden word"] = self.text
        base_stats["Remaining guesses"] = self.remaining_guesses
        return base_stats
