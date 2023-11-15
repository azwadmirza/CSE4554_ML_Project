    def __init__(self, signal1D):

        Component.__init__(self, ['yscale', 'xscale', 'shift'])

        self._position = self.shift
        self._whitelist['signal1D'] = ('init,sig', signal1D)
        self.signal = signal1D
        self.yscale.free = True
        self.yscale.value = 1.
        self.xscale.value = 1.
        self.shift.value = 0.

        self.prepare_interpolator()
        # Options
        self.isbackground = True
        self.convolved = False
        self.interpolate = True