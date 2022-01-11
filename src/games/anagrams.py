from collections import Counter
import pygame
from .game_utils import Timer
from .text_game import TextGame, TextInputObserver

MINIMUM_WORD_LENGTH = 3
EVT_WORD_SPELL = "spell_word"
EVT_CHECK_TIME = "check_time"


class Anagrams(TextGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(AnagramsObs())

    def handle_input(self, delta, input_state):
        super().handle_input(delta, input_state)
        if input_state.key_pressed(pygame.K_TAB):
            self.send_notification(EVT_WORD_SPELL)
        if input_state.key_pressed(pygame.K_SPACE):
            self.send_notification(EVT_CHECK_TIME)


class AnagramsObs(TextInputObserver):
    def __init__(self):
        super().__init__()
        self.anagram_word = ""
        self.letter_counts = None
        self.entered_anagrams = set()
        self.game_timer = None

    def handle_start(self, game, *args, **kwargs):
        super().handle_start(game, *args, **kwargs)
        self.anagram_word = game.context.word_db.fetch_random_word(8, 15, True)
        self.letter_counts = Counter(self.anagram_word)
        self.game_timer = Timer(self.set_win_state, 60)
        game.context.spm.output("Your word is: %s" % self.anagram_word)

    def is_char_matching(self, char):
        return super().is_char_matching(char) and self.text.count(
            char
        ) < self.letter_counts.get(char, 0)

    def handle_text_submit(self, game, *args, **kwargs):
        # The word must be long enough
        if len(self.text) < MINIMUM_WORD_LENGTH:
            game.context.spm.output(
                "Your word must be at least %s letter long" % MINIMUM_WORD_LENGTH
            )
        # Word can't be the same as `anagram_word`
        elif self.text == self.anagram_word:
            game.context.spm.output("The starting word does not count!")
        elif self.text in self.entered_anagrams:
            game.context.spm.output("You already guessed that")
        else:
            if not game.context.word_db.word_in_db(self.text):
                game.context.spm.output("Your anagram needs to be a valid word")
            else:
                self.entered_anagrams.add(self.text)
                # We subtract to add time
                self.game_timer.add_time(-3)
                game.context.spm.output("Next?")

        self.clear_text()
        return False

    def handle_frame_update(self, game, delta, *args, **kwargs):
        self.game_timer.update(delta)

    def handle_spell_word(self, game, *args, **kwargs):
        game.context.spm.output(", ".join(self.anagram_word))

    def handle_check_time(self, game, *args, **kwargs):
        game.context.spm.output("%d seconds" % self.game_timer.fetch_remaining_time())

    def gather_statistics(self):
        # Stub
        return {}
