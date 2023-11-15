    def __init__(self, n_workers=None, output_types=None, pure_depends=None, **kw):
        super().__init__(_n_workers=n_workers, _output_types=output_types,
                         _pure_depends=pure_depends, **kw)
        if self.output_types is None:
            self.output_types = [OutputType.object]