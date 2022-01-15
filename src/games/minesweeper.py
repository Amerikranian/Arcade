from enum import Enum
import math
import random
import pygame
from .grid_game import GridGame, GridGameObserver, LEFT, RIGHT, UP, DOWN

EVT_MINE_CHECK = "check_mines"
EVT_GRID_REVEAL = "reveal_pos"
EVT_TILE_CNT = "check_empty_tile_count"
EVT_LVL_SKIP = "skip_level"
EVT_TILE_MARK = "mark_tile"


class Minesweeper(GridGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(MinesweeperObs())

    def handle_input(self, delta, input_state):
        super().handle_input(delta, input_state)
        if input_state.key_pressed(pygame.K_RETURN):
            self.send_notification(EVT_MINE_CHECK)
        if input_state.key_pressed(pygame.K_SPACE):
            self.send_notification(EVT_GRID_REVEAL)
        if input_state.key_pressed(pygame.K_TAB):
            self.send_notification(EVT_TILE_CNT)
        if input_state.key_pressed(pygame.K_n):
            self.send_notification(EVT_LVL_SKIP)
        if input_state.key_pressed(pygame.K_m):
            self.send_notification(EVT_TILE_MARK)


class MinesweeperObs(GridGameObserver):
    def __init__(self):
        super().__init__(7, 7)
        self.mine_density = 0.4
        self.reveal_density = 0.4
        self.mine_dirs = (
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
        )
        self.total_empty_tiles = 0
        self.marked_tiles = set()

    def handle_start(self, game, *args, **kwargs):
        super().handle_start(game, *args, **kwargs)
        self.fill_grid()
        game.context.spm.output(self.fetch_tile_info(self.flatten(self.position)))

    def fill_grid(self):
        dims = self.dimensions[0] * self.dimensions[1]
        self.position = (0, 0)
        # We floor because rounding up any decimals will cause us to be over the desired ratio
        total_mines = math.floor(dims * self.mine_density)
        reveal_k = math.floor(dims * self.reveal_density)
        self.total_empty_tiles = dims - total_mines - reveal_k

        # Fill up grid
        self.grid = [
            TileEnum.mined if i < total_mines else TileEnum.empty for i in range(dims)
        ]
        # We reveal a certain percentage of empty tiles by considering the entries to the right of the last mine
        for k in random.sample(
            range(
                next(
                    i
                    for i in reversed(range(len(self.grid)))
                    if self.grid[i] == TileEnum.mined
                ),
                dims,
            ),
            reveal_k,
        ):
            self.grid[k] = TileEnum.seen

        random.shuffle(self.grid)

    def fetch_tile_info(self, index):
        # A quick check
        if index in self.marked_tiles:
            return "Marked"
        match self.grid[index]:
            case TileEnum.seen:
                return "Seen"
            case TileEnum.empty | TileEnum.mined:
                return "Hidden"
            case _:
                return "Unknown"

    def handle_grid_scroll(self, game, direction, *args, **kwargs):
        if not super().handle_grid_scroll(game, direction, *args, **kwargs):
            return False
        print(self.dimensions, self.position)
        game.context.spm.output(self.fetch_tile_info(self.flatten(self.position)))

    def fetch_adjacent_empty_tile_count(self):
        cnt = 0
        for p in self.mine_dirs:
            new_pos = self.position[0] + p[0], self.position[1] + p[1]
            if not self.in_bounds(new_pos):
                continue
            index = self.flatten(new_pos)
            if self.grid[index] == TileEnum.mined:
                cnt += 1

        return cnt

    def handle_check_mines(self, game, *args, **kwargs):
        index = self.flatten(self.position)
        if self.grid[index] != TileEnum.seen:
            game.context.spm.output("You have not revealed this tile yet")
        else:
            game.context.spm.output(str(self.fetch_adjacent_empty_tile_count()))

    def handle_reveal_pos(self, game, *args, **kwargs):
        index = self.flatten(self.position)
        match self.grid[index]:
            case TileEnum.seen:
                game.context.spm.output("This tile has already been revealed")
            case TileEnum.mined:
                self.set_lose_state()
            case TileEnum.empty:
                self.grid[index] = TileEnum.seen
                self.total_empty_tiles -= 1
                if self.total_empty_tiles == 0:
                    self.level_up()
                game.context.spm.output(str(self.fetch_adjacent_empty_tile_count()))

    def handle_check_empty_tile_count(self, game, *args, **kwargs):
        game.context.spm.output("%s tiles remaining" % self.total_empty_tiles)

    def level_up(self):
        # We keep this super super basic... for now
        self.reveal_density **= 1.1
        self.mine_density **= 0.93
        # We also grow the grid
        # We do so unevenly to lessen the difficulty curve
        # It's also possible the grid may not even grow
        dims_copy = list(self.dimensions)
        dims_copy[random.randint(0, len(self.dimensions) - 1)] += random.randint(0, 2)
        self.dimensions = tuple(dims_copy)
        self.fill_grid()

    def handle_skip_level(self, game, *args, **kwargs):
        # This is somewhat of an arbitrary number
        # Perhaps we'll make this percentage-based, too
        if self.total_empty_tiles <= 7:
            self.level_up()
            game.context.spm.output("Level skipped. New level generated")
            game.context.spm.output(
                self.fetch_tile_info(self.flatten(self.position)), False
            )
        else:
            game.context.spm.output("There are still plenty of tiles to find...")

    def handle_mark_tile(self, game, *args, **kwargs):
        index = self.flatten(self.position)
        if index in self.marked_tiles:
            self.marked_tiles.remove(index)
            game.context.spm.output("Unmarked")
        else:
            # We should only allow marking hidden tiles
            if self.grid[index] == TileEnum.seen:
                game.context.spm.output(
                    "There is no point in marking already-known tiles"
                )
            else:
                self.marked_tiles.add(index)
                game.context.spm.output("Marked")


class TileEnum(Enum):
    empty = 0
    seen = 1
    mined = 2
