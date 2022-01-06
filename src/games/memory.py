import random

import cytolk.tolk as tolk
import pygame
from .grid_game import GridGame, GridGameObserver, LEFT, RIGHT, UP, DOWN


class Memory(GridGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(MemoryObs())


class MemoryObs(GridGameObserver):
    def __init__(self):
        super().__init__(4, 4)
        self.revealed_word = None

    def handle_start(self, game, *args, **kwargs):
        super().handle_start(game, *args, **kwargs)
        words = game.context.word_db.fetch_random_words(3, 6, 8, False) * 2
        self.grid = words.copy()
        random.shuffle(self.grid)
        self.revealed = [
            False,
        ] * len(self.grid)
        tolk.output("Welcome!")

    def handle_grid_scroll(self, game, direction, *args, **kwargs):
        if not super().handle_grid_scroll(game, direction, *args, **kwargs):
            return False
        index = self.flatten(self.position)
        if self.revealed[index]:
            tolk.output(self.grid[index])
        else:
            tolk.output(str(self.position))
        return True

    def handle_grid_submit(self, game, *args, **kwargs):
        index = self.flatten(self.position)
        if self.revealed[index]:
            return
        if self.revealed_word == None:
            self.revealed_word = index
            self.revealed[index] = True
            tolk.output(f"Revealed {self.grid[index]}")
        else:
            tolk.output(f"Revealed {self.grid[index]}")
            self.revealed[index] = True
            if not self.grid[self.revealed_word] == self.grid[index]:
                tolk.output("No match")
                self.revealed[self.revealed_word] = False
                self.revealed[index] = False
            elif all([tile == True for tile in self.revealed]):
                self.set_win_state()
            self.revealed_word = None
