    def __init__(self, iterable=None):
        self._members = dict()
        if iterable:
            for o in iterable:
                self.add(o)