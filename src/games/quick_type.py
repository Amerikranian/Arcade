import pygame

from screen import Screen

from .text_game import TextGame, TextGameObserver


EVT_REPORT_WORD = "report_word"
EVT_REPORT_TIME = "report_time"


class QuickType(TextGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(QuickTypeObs())

    def handle_input(self, delta, input_state):
        super().handle_input(delta, input_state)
        if input_state.key_pressed(pygame.K_SPACE):
            self.send_notification(EVT_REPORT_WORD)
        elif input_state.key_pressed(pygame.K_TAB):
            self.send_notification(EVT_REPORT_TIME)


class QuickTypeObs(TextGameObserver):
    def __init__(self):
        super().__init__("^[a-z]$", True)
        self.game_timer = 60
        self.guess = ""
        self.word = None
        self.time_reward = 3
        self.time_penalty = 10

    def handle_start(self, game, *args, **kwargs):
        super().handle_start(game, *args, **kwargs)
        self.game = game
        return True

    def handle_text_unicode(self, game, char, difficulty, *args, **kwargs):
        if not self.is_char_matching(char):
            return False
        self.guess += char
        game.context.spm.output(char)
        if self.word.startswith(self.guess):
            if self.guess == self.word:
                self.game_timer += self.time_reward
                self.word = None
                self.game.play_wait_from_dir("correct")
        else:
            self.game_timer -= 5
            self.word = None
            self.game.play_wait_from_dir("incorrect")
        return True

    def handle_frame_update(self, game, delta, **kwargs):
        self.game_timer -= delta
        if self.game_timer <= 0:
            self.set_lose_state()
        elif not self.word:
            self.fetch_word()

    def handle_report_word(self, game, *args, **kwargs):
        game.context.spm.output(self.word)
        return True

    def handle_report_time(self, game, *args, **kwargs):
        time = round(self.game_timer)
        game.context.spm.output(f"{time} seconds remaining")
        return True

    def fetch_word(self):
        self.guess = ""
        self.word = self.game.context.word_db.fetch_random_word(
            3, self.game.difficulty + 5
        )
        self.game.context.spm.output(self.word)
