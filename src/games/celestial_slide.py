import random
import pygame

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

    def handle_start(self, game, *args, **kwargs):
        super().handle_start(game, *args, **kwargs)
        game.context.sounds.set_position((self.dimensions[0] // 2, 0.5, 0))
        game.context.spm.output("Welcome!")

    def handle_grid_scroll(self, game, direction, *args, **kwargs):
        if not super().handle_grid_scroll(game, direction, *args, **kwargs):
            return False
        index = self.flatten(self.position)
        if self.grid[index]:
            game.context.spm.output(self.grid[index])
        else:
            game.context.spm.output("Empty")
        x, z = self.position
        game.play_from_dir("grid_scroll", position=(x, 0, z))
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
            x, z = self.position
            game.play_from_dir("slide", position=(x, 0, z))
            return True
        return False

    def handle_grid_submit(self, game, *args, **kwargs):
        if self.grid[:-1] == self.initial_sequence:
            self.set_win_state()
        else:
            game.context.spm.output("Incomplete")
        return True
