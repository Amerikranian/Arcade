import random
import pygame

from .grid_game import GridGame, GridGameObserver, LEFT, RIGHT, UP, DOWN


EVT_TIME_CHECK = "time_check"


class Memory(GridGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(MemoryObs())

    def handle_input(self, delta, input_state):
        super().handle_input(delta, input_state)
        if input_state.key_pressed(pygame.K_t):
            self.send_notification(EVT_TIME_CHECK)


class MemoryObs(GridGameObserver):
    def __init__(self):
        super().__init__(4, 4)
        self.revealed_word = None
        self.timer = 0
        self.time_limit = 60

    @property
    def time_remaining(self):
        return round(self.time_limit - self.timer)

    def handle_start(self, game, *args, **kwargs):
        super().handle_start(game, *args, **kwargs)
        words = game.context.word_db.fetch_random_words(3, 6, 8, False) * 2
        self.grid = words.copy()
        random.shuffle(self.grid)
        self.revealed = [
            False,
        ] * len(self.grid)
        game.context.spm.output("Welcome!")

    def handle_grid_scroll(self, game, direction, *args, **kwargs):
        if not super().handle_grid_scroll(game, direction, *args, **kwargs):
            return False
        index = self.flatten(self.position)
        if self.revealed[index]:
            game.context.spm.output(self.grid[index])
        else:
            game.context.spm.output(str(self.position))
        return True

    def handle_grid_submit(self, game, *args, **kwargs):
        index = self.flatten(self.position)
        if self.revealed[index]:
            return
        if self.revealed_word == None:
            self.revealed_word = index
            self.revealed[index] = True
            game.context.spm.output(f"Revealed {self.grid[index]}")
        else:
            game.context.spm.output(f"Revealed {self.grid[index]}")
            self.revealed[index] = True
            if not self.grid[self.revealed_word] == self.grid[index]:
                game.context.spm.output("No match", False)
                self.revealed[self.revealed_word] = False
                self.revealed[index] = False
            elif all([tile == True for tile in self.revealed]):
                self.set_win_state()
            self.revealed_word = None

    def handle_frame_update(self, game, delta, **kwargs):
        self.timer += delta
        if self.time_remaining <= 0:
            self.set_lose_state()

    def handle_time_check(self, game, **kwargs):
        game.context.spm.output(f"{self.time_remaining} seconds remaining")
