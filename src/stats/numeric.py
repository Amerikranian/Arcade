from .statistics import NumericStatistic

# We assume that n is new population size
# Also, for any calculations, we assume that any offsets have been set correctly


class Number(NumericStatistic):
    """Expects one placeholder"""

    def __init__(self, o_str, value, r_digits=3):
        super().__init__(o_str, value, rnd_digits=r_digits)

    def eval(self):
        return self.value


class Mean(NumericStatistic):
    """Expects one placeholder"""

    def __init__(self, o_str, value, r_digits=3):
        super().__init__(o_str, value, rnd_digits=r_digits)

    def eval(self):
        return round(
            (self.given_offset * (self.n - 1) + self.value) / self.n, self.rnd_digits
        )


class Ratio(NumericStatistic):
    """A ratio of (value + given_offset) / n
    Expects two placeholders if one does not wish to see the percentage, three otherwise"""

    def __init__(self, o_str, value, r_digits=3, include_percentage=True):
        super().__init__(o_str, value, rnd_digits=r_digits)
        self.include_percentage = include_percentage

    def eval(self):
        a = self.value + self.given_offset
        if self.include_percentage:
            return a, self.n, round(a / self.n * 100, self.rnd_digits)
        return a, self.n
