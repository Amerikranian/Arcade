from keyboard import Keyboard
from screen import Screen, IS_ACTIVE


class ScreenManager:
    def __init__(self):
        self.input_state = Keyboard()
        self.screens = []

    def has_screens(self):
        return len(self.screens) > 0

    def add_screen(self, screen):
        screen.on_create()
        screen.set_screen_manager_instance(self)
        self.screens.append(screen)

    def remove_screen(self, screen):
        if screen in self.screens:
            self.screens.remove(screen)
        screen.on_destroy()

    def update(self, delta):
        self.input_state.update()
        # we make a copy of thew screen stack in case handling input removes screens or screens pop
        temp_screens = self.screens.copy()
        has_given_input = False
        for i in range(len(temp_screens) - 1, -1, -1):
            temp_screens[i].update(delta, i != len(self.screens) - 1)
            if not has_given_input and temp_screens[i].screen_status == IS_ACTIVE:
                # Only the first active screen receives input
                temp_screens[i].handle_input(delta, self.input_state)
                has_given_input = True
