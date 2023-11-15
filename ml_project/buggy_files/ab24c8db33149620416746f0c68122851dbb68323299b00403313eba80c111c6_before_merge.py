    def __init__(self, A=1e-5, r=3., origin=0., shift=20., ratio=1.,
                 **kwargs):
        super(DoublePowerLaw, self).__init__(
            expression="A * (ratio * (x - origin - shift) ** -r + (x - origin) ** -r)",
            name="DoublePowerLaw",
            A=A,
            r=r,
            origin=origin,
            shift=shift,
            ratio=ratio,
            position="origin",
            autodoc=True,
            **kwargs,
        )

        self.origin.free = False
        self.shift.value = 20.
        self.shift.free = False
        self.left_cutoff = 0.  # in x-units

        # Boundaries
        self.A.bmin = 0.
        self.A.bmax = None
        self.r.bmin = 1.
        self.r.bmax = 5.

        self.isbackground = True
        self.convolved = False