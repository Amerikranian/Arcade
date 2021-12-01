import pygame


class Keyboard:
    def __init__(self):
        self.current_key_presses = pygame.key.get_pressed()
        self.last_key_presses = self.current_key_presses
        self.quit_event = None
        self.keypress_event = None  # Text input purposes
        self.events = []

    def update(self):
        self.last_key_presses = self.current_key_presses
        self.current_key_presses = pygame.key.get_pressed()
        filtered_quit_events = pygame.event.get(eventtype=pygame.QUIT)
        self.quit_event = (
            None if len(filtered_quit_events) == 0 else filtered_quit_events[0]
        )
        filtered_keypress_events = pygame.event.get(eventtype=pygame.KEYDOWN)
        # Pygame seems to detect keys one at a time
        # We'll change this if it can be varified that event.get() can return multiple keys
        self.keypress_event = (
            None if len(filtered_keypress_events) == 0 else filtered_keypress_events[0]
        )
        # If needed, we'll extend this to mouse and gamepad
        # Group anything else into `self.events`
        self.events = pygame.event.get()

    def key_pressed(self, key):
        return self.current_key_presses[key] and not self.last_key_presses[key]

    def key_held(self, key):
        return self.current_key_presses[key]

    def key_released(self, key):
        return not self.current_key_presses[key] and self.last_key_presses[key]
