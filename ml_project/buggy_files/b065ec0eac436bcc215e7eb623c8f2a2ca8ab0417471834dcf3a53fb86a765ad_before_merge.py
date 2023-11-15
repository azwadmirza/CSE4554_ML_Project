    def __init__(self, size, color=None, ismask=False, duration=None):
        w, h = size
        shape = (h, w) if np.isscalar(color) else (h, w, len(color))
        super().__init__(
            np.tile(color, w * h).reshape(shape), ismask=ismask, duration=duration
        )