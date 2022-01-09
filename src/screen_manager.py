import logging
from keyboard import Keyboard
from screen import Screen, IS_ACTIVE

logger = logging.getLogger(__name__)


class ScreenManager:
    def __init__(self, ctx=None):
        self.input_state = Keyboard()
        self.screens = []
        # Screen queue is just a delayed method of pushing states
        # Since states can take time to quit, this is equivalent of "push the state onto the stack as soon as the state actually exits"
        # As expected, we have fifo order
        self.screen_queue = []
        self.context = ctx

    def has_screens(self):
        return len(self.screens) > 0

    def enqueue_screen(self, screen):
        self.screen_queue.append(screen)

    def dequeue_screen(self, screen):
        self.screen_queue.remove(screen)

    def is_screen_queue_empty(self):
        return len(self.screen_queue) == 0

    def add_screen(self, screen):
        # Do injection of `self` and `self.context` first
        # This is so that the screen has access to any resource storages on context
        screen.set_screen_manager_instance(self)
        screen.set_context(self.context)
        screen.on_create()
        self.screens.append(screen)

    def remove_screen(self, screen, use_queue=True):
        if screen in self.screens:
            self.screens.remove(screen)
        screen.on_destroy()

        if use_queue and not self.is_screen_queue_empty():
            queued_screen = self.screen_queue.pop(0)
            self.add_screen(queued_screen)

    def fetch_screen_from_top(self, offset):
        return self.screens[-offset]

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
