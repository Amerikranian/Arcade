from .statistics import NumericStatistic


class Number(NumericStatistic):
    """Expects one placeholder"""

    def __init__(self, o_str, value, r_digits=3):
        super().__init__(o_str, value, rnd_digits=r_digits)

    def eval(self):
        return self.value

    def update(self, value):
        self.value += value


class Mean(NumericStatistic):
    """Expects one placeholder"""

    def __init__(self, o_str, value, r_digits=3):
        super().__init__(o_str, value, rnd_digits=r_digits)

    def update(self, value, inc_n=1):
        self.value += value
        self.n += inc_n

    def eval(self):
        return round(self.value / self.n, self.rnd_digits)


class Ratio(NumericStatistic):
    """A ratio of value / n
    Expects two placeholders if one does not wish to see the percentage, three otherwise"""

    def __init__(self, o_str, value, r_digits=3, include_percentage=True):
        super().__init__(o_str, value, rnd_digits=r_digits)
        self.include_percentage = include_percentage

    def update(self, value, inc_n=1):
        self.value += value
        self.n += inc_n

    def eval(self):
        if self.include_percentage:
            return self.value, self.n, round(self.value / self.n * 100, self.rnd_digits)
        return self.value, self.n
