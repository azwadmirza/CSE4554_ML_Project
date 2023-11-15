    def _handle_size(cls, size):
        if size is None:
            return size
        try:
            return tuple(int(s) for s in size)
        except TypeError:
            return size,