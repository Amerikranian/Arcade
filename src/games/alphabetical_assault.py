import enum
import random
import pygame

from .game_utils import Timer
from .grid_game import GridGame, GridGameObserver, LEFT, RIGHT, UP, DOWN


EVT_REPORT_ACTIVE_LETTER = "report_active_letter"
EVT_REPORT_LETTERS_REMAINING = "report_letters_remaining"


class AlphabeticalAssault(GridGame):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.add_observer(AlphabeticalAssaultObs())

    def handle_input(self, delta, input_state):
        super().handle_input(delta, input_state)
        if input_state.key_pressed(pygame.K_TAB):
            self.send_notification(EVT_REPORT_ACTIVE_LETTER)
        elif input_state.key_pressed(pygame.K_l):
            self.send_notification(EVT_REPORT_LETTERS_REMAINING)


class AlphabeticalAssaultObs(GridGameObserver):
    def __init__(self):
        super().__init__(6, 6)
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.letter_distributions = {
            "A": 9,
            "B": 2,
            "C": 2,
            "D": 4,
            "E": 12,
            "F": 2,
            "G": 3,
            "H": 2,
            "I": 9,
            "J": 1,
            "K": 1,
            "L": 4,
            "M": 2,
            "N": 6,
            "O": 8,
            "P": 2,
            "Q": 1,
            "R": 6,
            "S": 4,
            "T": 6,
            "U": 4,
            "V": 2,
            "W": 2,
            "X": 1,
            "Y": 2,
            "Z": 1,
        }
        self.bag = []
        for letter in self.alphabet:
            self.bag.extend([letter] * self.letter_distributions[letter])
        random.shuffle(self.bag)
        self.active_letter = None
        self.last_landed_letter = None
        self.grid = [[None] * self.dimensions[1] for i in range(self.dimensions[0])]
        self.letter_spawning_speed = 1
        self.minimum_word_length = 3
        self.letter_falling_speed = 1.25
        self.letter_falling_timer = GameTimer(
            self.drop_active_letter,
            self.letter_falling_speed,
            True,
            lambda: self.active_letter != None,
        )
        self.letter_spawning_timer = GameTimer(
            self.spawn_letter,
            self.letter_spawning_speed,
            True,
            lambda: self.active_letter == None,
        )

    def handle_start(self, game, *args, **kwargs):
        self.game = game
        game.context.sounds.set_position(((self.dimensions[0] / 2) - 0.5, -0.5, 0))
        self.position = [0, self.dimensions[1] - 1]
        game.context.spm.output("Welcome!")

    def in_bounds(self, position):
        return not any(map(lambda x, y: x < 0 or x >= y, position, self.dimensions))

    def handle_grid_scroll(self, game, direction, *args, **kwargs):
        if not super().handle_grid_scroll(game, direction, *args, **kwargs):
            return False
        x, y = self.position
        if self.grid[x][y]:
            game.context.spm.output(f"{self.grid[x][y]}; {x+1}, {y+1}")
        else:
            game.context.spm.output(f"Empty; {x+1}, {y+1}")
        game.play_from_dir("grid_scroll", position=(x, 0, y))
        return True

    def handle_slide(self, game, direction, *args, **kwargs):
        if self.active_letter and direction != UP:
            direction = self.directions[direction]
            destination = list(map(lambda x, y: x + y, self.active_letter, direction))
            if self.in_bounds(destination) and self.is_open(destination):
                old_x, old_y = self.active_letter
                new_x, new_y = destination
                self.grid[old_x][old_y], self.grid[new_x][new_y] = (
                    self.grid[new_x][new_y],
                    self.grid[old_x][old_y],
                )
                self.active_letter = destination
                game.play_from_dir("slide", position=(new_x, 0, new_y))
                game.context.spm.output(f"{new_x+1}, {new_y+1}")

    def handle_frame_update(self, game, delta, **kwargs):
        self.letter_spawning_timer.update(delta)
        self.letter_falling_timer.update(delta)
        # loop through all of the letters and make sure they are grounded
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if (
                    self.grid[x][y]
                    and [x, y] != self.active_letter
                    and not self.is_grounded((x, y))
                ):
                    self.fall(
                        (x, y)
                    )  # if there's a floating letter on this tile of the grid that isn't our active letter, drop it down

    def handle_report_active_letter(self, game, **kwargs):
        if self.active_letter:
            x, y = self.active_letter
            game.context.spm.output(f"{self.grid[x][y]}; {x+1}, {y+1}")

    def handle_report_letters_remaining(self, game, **kwargs):
        game.context.spm.output(f"{len(self.bag)} letters remaining")

    def spawn_letter(self):
        new_letter = None
        possible_locations = (
            []
        )  # figure out which tiles on the top row are empty so we can pick one at random
        for x in range(self.dimensions[0]):
            if not self.grid[x][0]:  # if the tile is empty
                possible_locations.append([x, 0])  # Then we can consider using it
        if possible_locations:  # if there are valid choices to choose from
            location = random.choice(possible_locations)
            new_letter = self.bag.pop()
            self.active_letter = location
            self.grid[location[0]][location[1]] = new_letter
            self.game.play_from_dir("spawn", position=(location[0], 0, location[1]))
            self.game.context.spm.output(new_letter)
        else:
            self.set_lose_state()

    def drop_active_letter(self):
        if not self.is_grounded(self.active_letter):
            x, y = self.active_letter
            self.fall(self.active_letter)
            self.game.play_from_dir(
                "move",
                position=(x, 0, y),
                pitch_bend=1.5 - (y / len(self.grid[x]) + 0.5),
            )
            self.active_letter[1] += 1
        else:
            x, y = self.active_letter
            self.last_landed_letter = self.active_letter
            self.clear_word()
            self.active_letter = None
            self.game.play_from_dir("land", position=(x, 0, y))
            self.letter_spawning_timer.restart()
            if len(self.bag) <= 0:
                self.set_win_state()

    def fall(self, position):
        x, y = position
        self.grid[x][y], self.grid[x][y + 1] = self.grid[x][y + 1], self.grid[x][y]

    def is_grounded(self, position):
        x, y = position
        return not self.is_open((x, y + 1))

    def is_open(self, position):
        x, y = position
        if x < 0 or x >= self.dimensions[0]:
            return False
        if y < 0 or y >= self.dimensions[1]:
            return False
        return self.grid[x][y] == None

    def clear_word(self):
        x, y = self.active_letter
        word = self.find_longest_word((x, y))
        if word:
            self.game.play_from_dir("good")
            self.game.context.spm.output(self.positions_to_string(word).lower())
            for position in word:
                x, y = position
                self.grid[x][y] = None

    def longest_word_on_row(self, row):
        longest_word = []
        for i in range(self.minimum_word_length, len(self.grid)):
            for j in range(0, len(self.grid) - i + 1):
                positions = [[j + k, row] for k in range(i)]
                word = self.positions_to_string(positions)
                if (
                    not " " in word
                    and len(word) > len(longest_word)
                    and self.game.context.word_db.word_in_db(word)
                ):
                    longest_word = positions
        return longest_word

    def longest_word_on_column(self, column):
        longest_word = []
        for i in range(self.minimum_word_length, len(self.grid[column])):
            for j in range(0, len(self.grid[column]) - i + 1):
                positions = [[column, j + k] for k in range(i)]
                word = self.positions_to_string(positions)
                if (
                    not " " in word
                    and len(word) > len(longest_word)
                    and self.game.context.word_db.word_in_db(word.lower())
                ):
                    longest_word = positions
        return longest_word

    def positions_to_string(self, positions):
        string = ""
        for position in positions:
            x, y = position
            string += self.grid[x][y] if self.grid[x][y] else " "
        return string

    def find_longest_word(self, position):
        x, y = position
        results = (self.longest_word_on_row(y), self.longest_word_on_column(x))
        word = max(results, key=lambda x: len(x))
        return word if word else None


class GameTimer(Timer):
    def __init__(self, clb, fire_time, should_repeat=True, condition=None):
        Timer.__init__(self, clb, fire_time, should_repeat)
        self.condition = condition

    def restart(self):
        self.elapsed = 0

    def update(self, delta):
        if self.clb is None:
            return
        self.elapsed += delta
        if self.elapsed >= self.fire_time:
            if not self.condition or self.condition():
                self.trigger()
