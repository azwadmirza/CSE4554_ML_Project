    def _get_tick_frac_labels(self):
        # This conditional is currently unnecessary since we only support
        # linear, but eventually we will support others so we leave it in
        if (self.axis.scale_type == 'linear'):

            major_num = 11  # maximum number of major ticks
            minor_num = 4   # maximum number of minor ticks per major division

            major, majstep = np.linspace(0, 1, num=major_num, retstep=True)

            # XXX TODO: this should be better than just str(x)
            labels = [str(x) for x in 
                      np.interp(major, [0, 1], self.axis.domain)]

            # XXX TODO: make these nice numbers only
            # - and faster! Potentially could draw in linspace across the whole
            # axis and render them before the major ticks, so the overlap
            # gets hidden. Might be messy. Benchmark trade-off of extra GL
            # versus extra NumPy.
            minor = []
            for i in np.nditer(major[:-1]):
                minor.extend(np.linspace(i, (i + majstep),
                             (minor_num + 2))[1:-1])
        # elif (self.scale_type == 'logarithmic'):
        #     return NotImplementedError
        # elif (self.scale_type == 'power'):
        #     return NotImplementedError
        return major, minor, labels