    def __init__(self, size, color=None, ismask=False, duration=None):
        w, h = size

        if ismask:
            shape = (h, w)
            if color is None:
                color = 0
            elif not np.isscalar(color):
                raise Exception("Color has to be a scalar when mask is true")
        else:
            if color is None:
                color = (0, 0, 0)
            elif not hasattr(color, "__getitem__"):
                raise Exception("Color has to contain RGB of the clip")
            shape = (h, w, len(color))

        super().__init__(
            np.tile(color, w * h).reshape(shape), ismask=ismask, duration=duration
        )