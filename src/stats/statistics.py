class Statistic:
    """A general statistic, used as a base for its successors
    The basic idea is to inherit this, provide output strings, and override the eval function to return as many placeholders as `output_str` contains"""

    def __init__(self, output_str):
        self.output_str = output_str

    def __repr__(self):
        return self.output_str % self.eval()

    def eval(self):
        raise NotImplementedError("No evaluation possible for this statistic")

    def update(self, value):
        pass

    def save(self):
        """Persist the statistic. Do not export"""
        pass


class TextStatistic(Statistic):
    """A way to provide textual information, such as the hidden word in Hangman"""

    def __init__(self, output_str, txt):
        super().__init__(output_str)
        self.text = txt


class NumericStatistic(Statistic):
    """A statistic designed to calculate mean and the like"""

    def __init__(self, output_str, value, n=0, rnd_digits=3):
        super().__init__(output_str)
        self.value = value
        self.new_value = 0
        # Population size
        self.n = n
        # How much should we round to
        self.rnd_digits = rnd_digits
