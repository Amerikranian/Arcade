from observer import Observer, Subject
from screen import Screen


class Game(Screen):
    """A base game class, serving as both of a subject and an observer.
    The purpose of doing this is so that the game could focus on handling user input and send out events for different user actions.
    The basic idea is to inherit this class and override any method from the Screen class. Following this, import this in __init__.py, fix any issues, and repeat for subsequent creations.
    Each game's docstring will be used when the user clicks "Help" option in the game menu, split on newlines
    Each game may have a list of variations, and each variation may have its own number of difficulty modes, as described by the info.json file located within the data/GameName/.
    Please note that the name of the class, such as Hangman, Chess, etc, will be used both within the game menu (I.e, when the user scrolls over the object), and the data directory lookup.
    So, if the class is called Hangman, then the menu entry would read "Hangman", and any information stored within the game would be expected to be located in data/games/info.json under the key Hangman
    In addition, calling notify on game will attach the "variation" and "difficulty" parameters to any event, allowing observers to adjust to the selected mode and difficulty
    Each variation is expected to be a string, such as "Partial Anagrams", and the difficulties are expected to be integers with no specific constraints
    Variations and difficulties will be converted to their string equivalents, as either supplied by the creator or inferred by the program in the latter's case
    If no variation is provided, it is assumed that the game behaves in standard mode.
    If not specified otherwise, each variation will have 3 default difficulties.
    Creators can use empty quotation marks rather than a variation name to refer to the standard variation
    """

    def __init__(self, variation, difficulty):
        super().__init__()
        # Possibly change to multi inheritance?
        self.subject = Subject()
        self.variation = variation
        self.difficulty = difficulty

    def send_notification(self, event_type, *args, **kwargs):
        """Sends notifications to any observers, injecting variation, difficulty, and context.
        For now, we don't inject `self` because doing so encourages storage of state on the game.
        This may be subject to change
        """
        self.subject.notify(
            event_type, variation=self.variation, difficulty=self.difficulty, ctx=self.context, **kwargs
        )

