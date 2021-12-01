IS_TRANSITIONING_TO_BEING_ACTIVE = 0
IS_TRANSITIONING_TO_BEING_INACTIVE = 1
IS_ACTIVE = 2
IS_IDLE = 3


class Screen:
    def __init__(self):
        self.screen_manager = None
        self.screen_status = IS_TRANSITIONING_TO_BEING_ACTIVE
        self.is_exiting = (
            False  # Dictates whether the screen will go away after transitioning off
        )
        self.context = None

    def set_screen_manager_instance(self, scr):
        self.screen_manager = scr

    def set_context(self, ctx):
        self.context = ctx

    def on_create(self):
        """Called when the screen is pushed onto the stack"""
        pass

    def on_destroy(self):
        """Called when the screen is popped off the stack"""
        pass

    def get_progress_of_enter_transition(self, delta):
        """Called to determine whether a state has finished transitioning for entrance purposes"""
        return False

    def get_progress_of_exit_transition(self, delta):
        """Called to determine whether a state has finished transitioning for exit purposes"""
        return False

    def exit(self):
        self.is_exiting = True
        self.screen_status = IS_TRANSITIONING_TO_BEING_INACTIVE

    def update(self, delta, is_covered_by_another_screen):
        """Called regardless of the screen being covered by other screens"""
        if is_covered_by_another_screen and self.screen_status == IS_ACTIVE:
            # We're hidden by another screen, so we should transition off
            self.screen_status = IS_TRANSITIONING_TO_BEING_INACTIVE
        elif (
            not self.is_exiting
            and not is_covered_by_another_screen
            and self.screen_status != IS_ACTIVE
        ):
            self.screen_status = IS_TRANSITIONING_TO_BEING_ACTIVE

        # If we're transitioning, call the appropriate callback
        if self.screen_status == IS_TRANSITIONING_TO_BEING_ACTIVE:
            if not self.get_progress_of_enter_transition(delta):
                self.screen_status = IS_ACTIVE
        elif self.screen_status == IS_TRANSITIONING_TO_BEING_INACTIVE:
            if not self.get_progress_of_exit_transition(delta):
                if self.is_exiting:
                    self.screen_manager.remove_screen(self)
                else:
                    self.screen_status = IS_IDLE

    def handle_input(self, delta, input_state):
        pass
