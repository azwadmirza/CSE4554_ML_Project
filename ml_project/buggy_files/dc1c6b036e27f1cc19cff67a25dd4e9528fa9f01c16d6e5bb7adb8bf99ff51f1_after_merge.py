    def __init__(self, iterable=None):
        self._members = dict()
        if iterable:
            self.update(iterable)