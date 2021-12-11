import pygame.locals as pl
from cytolk import tolk
from screen import Screen


class MenuItem:
    def __init__(self, name, item_callback, should_exit):
        self.name = name
        self.item_callback = item_callback
        self.should_exit = should_exit

    def __repr__(self):
        return self.name

    def invoke(self, menu_instance):
        if self.should_exit:
            menu_instance.exit()
        self.item_callback(menu_instance)


class Menu(Screen):
    def __init__(self):
        super().__init__()
        self.intro_message = ""
        self.items = []
        self.cursor_position = 0

    def set_intro_message(self, msg):
        self.intro_message = msg

    def add_item(self, name, callback, should_exit=False):
        if not callable(callback):
            raise ValueError(
                "The provided item, %s, must have a callable callback" % name
            )
        self.items.append(MenuItem(name, callback, should_exit))

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
