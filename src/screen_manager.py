from keyboard import Keyboard
from screen import Screen, IS_ACTIVE


class ScreenManager:
    def __init__(self, ctx=None):
        self.input_state = Keyboard()
        self.screens = []
        self.context = ctx

    def has_screens(self):
        return len(self.screens) > 0

    def add_screen(self, screen):
        # Do injection of `self` and `self.context` first
        # This is so that the screen has access to any resource storages on context
        screen.set_screen_manager_instance(self)
        screen.set_context(self.context)
        screen.on_create()
        self.screens.append(screen)

    def remove_screen(self, screen):
        if screen in self.screens:
            self.screens.remove(screen)
        screen.on_destroy()

    def clear_all_screens(self, is_forced):
        for s in self.screens[::-1]:
            if is_forced:
                self.remove_screen(s)
            else:
                s.exit()

    def update(self, delta):
        self.input_state.update()
        if self.input_state.quit_event:
            self.clear_all_screens(True)

        # we make a copy of the screen stack in case handling input removes screens or screen updates cause them to pop
        temp_screens = self.screens.copy()
        has_given_input = False
        for i in range(len(temp_screens) - 1, -1, -1):
            temp_screens[i].update(delta, i != len(self.screens) - 1)
            if not has_given_input and temp_screens[i].screen_status == IS_ACTIVE:
                # Only the first active screen receives input
                temp_screens[i].handle_input(delta, self.input_state)
                has_given_input = True
