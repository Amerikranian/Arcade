import pygame
from game_menus import QuitMenu, StatisticsMenu
from observer import Observer
from .base_game import Game

EVT_GAME_STARTED = "start"
EVT_GAME_ENDED = "end"
EVT_REQUEST_QUIT = "menu_quit"


class ObservableGame(Game):
    def __init__(self, variation, difficulty):
        super().__init__(variation, difficulty)
        self.observers = []

    def add_observer(self, o):
        self.observers.append(o)

    def remove_observer(self, o):
        self.observers.remove(o)

    def send_notification(self, event_type, *args, **kwargs):
        for o in self.observers:
            o.notify(
                event_type,
                variation=self.variation,
                difficulty=self.difficulty,
                game=self,
                *args,
                **kwargs,
            )

            if o.has_ended():
                # We notify the observer one more time and quit
                # Will probably be changed when sounds are added
                o.notify(
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


class GameObserver(Observer):
    """An observer designed to handle logic within games.
    Provides convenient wrappers to extract callers from arguments as well as handle dispatching of events for differing variations
    Event handlers must be able to accept game as their first parameter
    """

    def fetch_dynamic_attr(self, attr, variation):
        # Make variation a valid match string
        variation = variation.lower().replace(" ", "_")
        func_list = []
        # We support logic functions that look like handle_partial_submit, where submit is event type and partial is the game varient
        # The downside to this is needing to update code when the variation is renamed
        # The alternative was to treat variations as integers
        if len(variation) > 0:
            attr_var_name = f"handle_{variation}_{attr}"
            if hasattr(self, attr_var_name):
                func_list.append(getattr(self, attr_var_name))
        attr_name = f"handle_{attr}"
        if hasattr(self, attr_name):
            func_list.append(getattr(self, attr_name))

        if len(func_list) == 0:
            return [self.handle_event]
        else:
            return func_list

    def notify(self, event_type, *args, **kwargs):
        if "game" in kwargs:
            context = kwargs.pop("game")
        else:
            context = None
        func_list = self.fetch_dynamic_attr(event_type, kwargs.get("variation", ""))
        for f in func_list:
            if not f(context, *args, **kwargs):
                break

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
