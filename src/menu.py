import pygame.locals as pl
from cytolk import tolk
from screen import Screen


class MenuItem:
    def __init__(self, name, item_callback):
        self.name = name
        self.item_callback = item_callback

    def __repr__(self):
        return self.name

    def invoke(self, menu_instance):
        self.item_callback(menu_instance)


class Menu(Screen):
    def __init__(self, items):
        super().__init__()
        # Items must be dicts of name: callback
        self.items = []
        for name, clb in items.items():
            self.add_item(name, clb)

        self.cursor_position = 0

    def add_item(self, name, callback):
        if not callable(callback):
            raise ValueError(
                "The provided item, %s, must have a callable callback" % name
            )
        self.items.append(MenuItem(name, callback))

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

    def handle_input(self, delta, input_state):
        if input_state.key_pressed(pl.K_UP):
            self.scroll(-1)
        elif input_state.key_pressed(pl.K_DOWN):
            self.scroll(1)
        elif input_state.key_pressed(pl.K_RETURN):
            self.activate_item()
