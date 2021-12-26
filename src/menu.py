import pygame.locals as pl
from cytolk import tolk
from screen import Screen


class MenuItem:
    def __init__(
        self, name, item_callback, callback_args, should_exit, should_include_self
    ):
        self.name = name
        self.callback_args = callback_args
        # Callbacks must accept at least one parameter, the menu instance
        # Callbacks can also be None, in which case the menu item could either exit or do nothing
        self.item_callback = item_callback
        self.should_exit = should_exit
        self.should_include_self = should_include_self

    def __repr__(self):
        return self.name

    def invoke(self, menu_instance):
        if self.should_exit:
            menu_instance.exit()
        if self.item_callback is not None:
            if self.should_include_self:
                self.item_callback(menu_instance, self.callback_args)
            else:
                self.item_callback(menu_instance)


class Menu(Screen):
    def __init__(self):
        super().__init__()
        self.intro_message = ""
        self.items = []
        self.cursor_position = 0

    def set_intro_message(self, msg):
        self.intro_message = msg

    def add_item(
        self,
        name,
        callback,
        callback_args=None,
        should_exit=False,
        should_include_self=False,
    ):
        if callback is not None and not callable(callback):
            raise ValueError(
                "The provided item, %s, must have a callable callback or be `None`"
                % name
            )
        self.items.append(
            MenuItem(name, callback, callback_args, should_exit, should_include_self)
        )

    def add_item_without_callback(self, name, should_exit=True):
        # A shortcut for adding the "Go back" option or alike
        self.add_item(name, None, should_exit=should_exit)

    def add_items(self, items):
        for k, v in items.items():
            self.add_item(k, v)

    def focus_item(self):
        # Will probably become function on `MenuItem` at some point
        tolk.output(str(self.items[self.cursor_position]))

    def activate_item(self):
        self.items[self.cursor_position].invoke(self)

    def scroll(self, direction):
        temp = self.cursor_position + direction
        # We don't bother wrapping, for now
        if temp < 0:
            temp = 0
        elif temp >= len(self.items) - 1:
            temp = len(self.items) - 1

        if temp != self.cursor_position:
            self.cursor_position = temp
            self.focus_item()

    def get_progress_of_enter_transition(self, delta):
        if self.intro_message:
            tolk.output(self.intro_message, True)
        self.focus_item()
        return False

    def handle_input(self, delta, input_state):
        if input_state.key_pressed(pl.K_UP):
            self.scroll(-1)
        elif input_state.key_pressed(pl.K_DOWN):
            self.scroll(1)
        elif input_state.key_pressed(pl.K_RETURN):
            self.activate_item()
