    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quadrature = GaussHermiteQuadrature1D()