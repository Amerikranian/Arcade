PRIMITIVE_TYPES = (str, int, float, bool)


class Statistic:
    """A general statistic, used as a base for its successors
    Currently does not support verifying valid message strings, I.e, the amount of given placeholders vs. the arguments spat out by eval"""

    def __repr__(self):
        return str(self.eval())

    def eval(self):
        raise NotImplementedError("No evaluation possible for this statistic")

    def update(self, value):
        pass

    def to_json(self):
        """Dumps all of the non-private attributes of the class to a dict
        Will not work with complex objects, more complex stats will need to override this to provide any modifications"""
        return {
            attr: getattr(self, attr)
            for attr in filter(
                lambda p: not p.startswith("_")
                and type(getattr(self, p)) in PRIMITIVE_TYPES,
                dir(self),
            )
        }

    def from_json(self, attrs):
        """Tries to match the given attributes to those on self, complaining when lookup fails"""
        for attr, val in attrs.items():
            if not hasattr(self, attr):
                raise ValueError(
                    'Failed to load attribute "%s" on the given statistic' % attr
                )
            else:
                setattr(self, attr, val)


class NumericStatistic(Statistic):
    """A statistic designed to calculate mean and the like"""

    def __init__(self, value=0, n=0, rnd_digits=3):
        self.value = value
        # Population size
        self.n = n
        # How much should we round to
        self._rnd_digits = rnd_digits
