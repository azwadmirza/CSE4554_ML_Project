    def __init__(self, universe, selection1, selection2, t0, tf, dtmax,
                 nproc=1):
        self.universe = universe
        self.selection1 = selection1
        self.selection2 = selection2
        self.t0 = t0
        self.tf = tf - 1
        self.dtmax = dtmax
        self.nproc = nproc
        self.timeseries = None