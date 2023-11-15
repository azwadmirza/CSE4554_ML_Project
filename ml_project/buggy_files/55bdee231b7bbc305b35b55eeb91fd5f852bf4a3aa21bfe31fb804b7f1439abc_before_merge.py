    def __init__(self, n_workers=None, output_types=None, **kw):
        super().__init__(_n_workers=n_workers, _output_types=output_types, **kw)
        if self.output_types is None:
            self.output_types = [OutputType.object]