class Observer:
    """Dummy class, mostly used to handle dynamic method dispatch."""

    def fetch_dynamic_attr(self, attr):
        """A wrapper testing existence of the given events and using the fallback on failure"""
        attr_name = f"handle_{event_type}_event"
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        return self.handle_event

    def handle_event(self, *args, **kwargs):
        """Fallback for dynamic method lookup"""
        pass

    def notify(self, event_type, *args, **kwargs):
        self.fetch_dynamic_attr(*args, **kwargs)


class Subject:
    def __init__(self):
        # A dict of event strings and lists of observers interested in those events
        self.observers = {}

    def add_observer(self, event, obs):
        if event not in self.observers:
            self.observers[event] = []
        self.observers[event].append(obs)

    def add_observer_to_events(self, events, obs):
        for e in events:
            self.add_observer(e)

    # Should be changed to be noisy when handling failures
    def remove_observer(self, event, obs):
        if event not in self.observers or obs not in self.observers[event]:
            return False
        self.observers[event].remove(obs)
        return True

    # Should be changed to be noisy when handling failures
    def remove_observer_from_events(self, events, obs):
        return all([self.remove_observer(e, obs) for e in events])

    # This isn't preferable, but will do in a pinch
    # Ideally we'd know what the observer is listening for
    def remove_observer_from_all_events(self, obs):
        return any([self.remove_observer(e, obs) for e in self.events])

    def notify(self, event_type, *args, **kwargs):
        if event_type not in self.observers:
            return False
        # Should probably be modified to support event propagation
        # I.e, if a notify method returns True for a given subject, we stop at user behest
        for o in self.observers[event_type]:
            # An observer could be interested in multiple events
            o.notify(event_type, *args, **kwargs)
