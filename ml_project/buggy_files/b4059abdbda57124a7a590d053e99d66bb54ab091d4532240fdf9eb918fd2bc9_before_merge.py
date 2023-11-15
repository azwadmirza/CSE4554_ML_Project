    def __init__(self, frac, default_len=10, charset=UTF):
        assert 0 <= frac <= 1
        assert default_len > 0
        self.frac = frac
        self.default_len = default_len
        self.charset = charset