    def __init__(self, frac, default_len=10, charset=UTF):
        if not (0 <= frac <= 1):
            warn("clamping frac to range [0, 1]", TqdmWarning, stacklevel=2)
            frac = max(0, min(1, frac))
        assert default_len > 0
        self.frac = frac
        self.default_len = default_len
        self.charset = charset