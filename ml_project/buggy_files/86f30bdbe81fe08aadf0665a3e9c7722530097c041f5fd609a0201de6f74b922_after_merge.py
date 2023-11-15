    def __init__(self, signal1D, yscale=1.0, xscale=1.0, shift=0.0, interpolate=True):

        Component.__init__(self, ['yscale', 'xscale', 'shift'])

        self._position = self.shift
        self._whitelist['signal1D'] = ('init,sig', signal1D)
        self.signal = signal1D
        self.yscale.free = True
        self.yscale.value = yscale
        self.xscale.value = xscale
        self.shift.value = shift

        self.prepare_interpolator()
        # Options
        self.isbackground = True
        self.convolved = False
        self.interpolate = interpolate