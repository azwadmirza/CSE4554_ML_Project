    def __init__(self, *args, **kwargs):
        warnings.warn(
            "PyroVariationalGP has been renamed to PyroGP.",
            DeprecationWarning
        )
        super().__init__(*args, **kwargs)