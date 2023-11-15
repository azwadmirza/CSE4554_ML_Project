    def __init__(self, hidDevice, *, is_hw1: bool = False):
        self.dongleObject = btchip(hidDevice)
        self.preflightDone = False
        self._is_hw1 = is_hw1