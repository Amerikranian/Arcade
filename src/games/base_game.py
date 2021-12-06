from observer import Observer
from screen import Screen


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
        return False


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
    Creators can use empty quotation marks rather than a variation name to refer to the standard variation
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
            self.exit()
