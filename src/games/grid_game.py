import pygame
from .observable_game import ObservableGame, GameObserver

EVT_GRID_SUBMIT = "grid_submit"
EVT_SCROLL = "grid_scroll"
EVT_SLIDE = "slide"
LEFT, RIGHT, UP, DOWN = 0, 1, 2, 3


class GridGame(ObservableGame):
    """A class designed to simplify creation of grid-based games, such as TicTacToe"""

    def handle_input(self, delta, input_state):
        direction = None
        if input_state.key_pressed(pygame.K_LEFT):
            direction = LEFT
        elif input_state.key_pressed(pygame.K_RIGHT):
            direction = RIGHT
        elif input_state.key_pressed(pygame.K_UP):
            direction = UP
        elif input_state.key_pressed(pygame.K_DOWN):
            direction = DOWN
        if not direction == None:
            if input_state.key_held(pygame.K_LSHIFT) or input_state.key_held(
                pygame.K_RSHIFT
            ):
                self.send_notification(EVT_SLIDE, direction=direction)
            else:
                self.send_notification(EVT_SCROLL, direction=direction)

        # We also check for user wanting to select the currently focused tile
        if input_state.key_pressed(pygame.K_RETURN):
            self.send_notification(EVT_GRID_SUBMIT)

        super().handle_input(delta, input_state)


class GridGameObserver(GameObserver):
    def __init__(self, length=10, width=10):
        super().__init__()
        self.dimensions = (length, width)
        self.position = (0, 0)
        self.directions = ((-1, 0), (1, 0), (0, -1), (0, 1))

    def handle_grid_scroll(self, game, direction, *args, **kwargs):
        new_position = list(
            map(lambda x, y: x + y, self.position, self.directions[direction])
        )
        if self.in_bounds(new_position):
            self.position = new_position
            return True
        return False

    def in_bounds(self, position):
        return not any(map(lambda x, y: x < 0 or x >= y, position, self.dimensions))

    def handle_slide(self, game, direction, *args, **kwargs):
        pass

    def flatten(self, position):
        """returns a 1d index given a 2d position"""
        return self.dimensions[-1] * position[-1] + position[0]
