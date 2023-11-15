    def _handle_size(cls, size):
        if size is None:
            return size
        try:
            return tuple(size)
        except TypeError:
            return size,