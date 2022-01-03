import random

import cytolk.tolk as tolk
import pygame

from enum import Enum

from .grid_game import GridGame, GridGameObserver, LEFT, RIGHT, UP, DOWN


class CelestialSlide(GridGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(CelestialSlideObs())


class CelestialSlideObs(GridGameObserver):
    def __init__(self):
        super().__init__(3, 3)
        self.initial_sequence = [
            "Mercury",
            "Venus",
            "Earth",
            "Mars",
            "Jupiter",
            "Saturn",
            "Uranus",
            "Neptune",
        ]
        self.grid = self.initial_sequence.copy()
        random.shuffle(self.grid)
        self.grid.append(None)
        self.state = GameStateEnum.running

    def handle_start(self, game, *args, **kwargs):
        tolk.output("Welcome!")

    def handle_grid_scroll(self, game, direction, *args, **kwargs):
        if not super().handle_grid_scroll(game, direction, *args, **kwargs):
            return False
        index = self.flatten(self.position)
        if self.grid[index]:
            tolk.output(self.grid[index])
        else:
            tolk.output("Empty")
        return True

    def handle_slide(self, game, direction, *args, **kwargs):
        new_position = list(
            map(lambda x, y: x + y, self.position, self.directions[direction])
        )
        position, destination = self.flatten(self.position), self.flatten(new_position)
        if self.in_bounds(new_position) and self.grid[destination] == None:
            self.grid[position], self.grid[destination] = (
                self.grid[destination],
                self.grid[position],
            )
            self.position = new_position
            tolk.output("*Sliding sound*")
            return True
        return False

    def handle_grid_submit(self, game, *args, **kwargs):
        if self.grid[:-1] == self.initial_sequence:
            tolk.output("Complete")
            self.state = GameStateEnum.won
        else:
            tolk.output("Incomplete")
        return True

    def has_won(self):
        return self.state == GameStateEnum.won

    def has_lost(self):
        return self.state == GameStateEnum.lost


class GameStateEnum(Enum):
    running = 0
    won = 1
    lost = 2
