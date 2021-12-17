class StatAggregator:
    """A container for the created statistics"""

    def __init__(self):
        self.stats = {}

    def add_stat(self, title, stat):
        if title in self.stats:
            raise ValueError('The statistic with the name "%s" already exists' % title)
        self.stats[title] = stat

    def remove_stat(self, title):
        if title not in self.stats:
            raise ValueError('The statistic with the name "%s" does not exist' % title)
        return self.stats.pop(title)

    def yield_stat_items_in_order(self, order):
        for o in order:
            if o not in self.stats:
                raise ValueError('The requested stat, "%s", does not exist' % o)
            yield self.stats[o]

    def yield_stat_items(self):
        for k in self.stat_items:
            yield self.stats[k]
