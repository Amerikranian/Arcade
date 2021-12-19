import pygame
from game_menus import QuitMenu, StatisticsMenu
from observer import Observer
from screen import Screen

EVT_GAME_STARTED = "start"
EVT_GAME_ENDED = "end"
EVT_REQUEST_QUIT = "menu_quit"


class GameObserver(Observer):
    """An observer designed to handle logic within games.
    Provides convenient wrappers to extract callers from arguments as well as handle dispatching of events for differing variations
    Event handlers must be able to accept game as their first parameter
    """

    def fetch_dynamic_attr(self, attr, variation):
        # If the variation is empty, no point in constructing event query
        if variation == "":
            return super().fetch_dynamic_attr(attr)

        # We support logic functions that look like handle_submit_partial, where submit is event type and partial is the game varient
        # The downside to this is needing to update code when the variation is renamed
        # The alternative was to treat variations as integers
        attr_name = f"handle_{attr}_{variation}"
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        return super().fetch_dynamic_attr(attr)

    def notify(self, event_type, *args, **kwargs):
        if "game" in kwargs:
            context = kwargs.pop("game")
        else:
            context = None
        self.fetch_dynamic_attr(event_type, kwargs.get("variation", ""))(
            context, *args, **kwargs
        )

    def has_ended(self):
        """Determines whether the given game has come to a conclusion"""
        return self.has_won() or self.has_lost()

    def gather_statistics(self):
        """Called at the end of the game to generate game statistics. Anything is valid as long as keys / values can be dumped into json. The dictionary must contain stat_items, and can also contain s_intro and include_statistics. See StatisticsMenu for further details"""
        return {
            "wins": int(self.has_won()),
            "losses": int(self.has_lost()),
            "Conclusion": "Success" if self.has_won() else "Failure",
        }

    # The next two functions are expected to return quickly and should not involve heavy computation
    # This is because they are called whenever the game is dispatching any events
    def has_lost(self):
        return False

    def has_won(self):
        return False

    def win(self):
        pass

    def lose(self):
        pass

    def run_cleanup(self):
        """Called at the end of the game, regardless of win/lose status"""
        pass

    def handle_end(self, game, variation, difficulty, *args, **kwargs):
        self.run_cleanup()
        if kwargs.get("quit_flag", False):
            game.screen_manager.fetch_screen_from_top(2).exit()
            return

        if self.has_won():
            self.win()
        else:
            self.lose()
        game.screen_manager.add_screen(
            StatisticsMenu(
                self.gather_statistics(), variation=variation, difficulty=difficulty
            )
        )

    def handle_menu_quit(self, game, *args, **kwargs):
        game.screen_manager.add_screen(QuitMenu(EVT_GAME_ENDED))


class Game(Screen):
    """A base game class, serving as both of a subject.
    The purpose of doing this is so that the game could focus on handling user input and send out events for different user actions.
    The basic idea is to inherit this class and override any method from the Screen class. Following this, import this in __init__.py, fix any issues, and repeat for subsequent creations.
    Each game may have a list of variations, and each variation may have its own number of difficulty modes, as described by the info.json file located within the data/games/.
    Please note that the name of the class, such as Hangman, Chess, etc, will be used both within the game menu (I.e, when the user scrolls over the object), and the data directory lookup.
    So, if the class is called Hangman, then the menu entry would read "Hangman", and any information stored within the game would be expected to be located in data/games/info.json under the key Hangman
    In addition, calling notify on game will attach the "variation" and "difficulty" parameters to any event, allowing observers to adjust to the selected mode and difficulty
    Each variation is expected to be a string, such as "Partial Anagrams", and the difficulties are expected to be integers with no specific constraints. Note that for the purposes of handling variations in code, if the variation contains spaces, they will be replaced by underscores (_)
    Variations and difficulties will be converted to their string equivalents, as either supplied by the creator or inferred by the program in the latter's case
    If no variation is provided, it is assumed that the game behaves in standard mode.
    If not specified otherwise, each variation will have 3 default difficulties.
    """

    def __init__(self, variation, difficulty, obs):
        super().__init__()
        self.observer = obs
        self.variation = variation
        self.difficulty = difficulty

    def send_notification(self, event_type, *args, **kwargs):
        self.observer.notify(
            event_type,
            variation=self.variation,
            difficulty=self.difficulty,
            game=self,
            *args,
            **kwargs,
        )

        if self.observer.has_ended():
            # We notify the observer one more time and quit
            # Will probably be changed when sounds are added
            self.observer.notify(
                EVT_GAME_ENDED,
                variation=self.variation,
                difficulty=self.difficulty,
                game=self,
                *args,
                **kwargs,
            )
            self.exit()

    def on_create(self):
        """Quick wrapper to send out start event"""
        self.send_notification(EVT_GAME_STARTED)

    def handle_input(self, delta, input_state):
        """Generic game keys"""
        if input_state.key_pressed(pygame.K_ESCAPE):
            self.send_notification(EVT_REQUEST_QUIT)
