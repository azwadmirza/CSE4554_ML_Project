    def __init__(self, *args, **kwargs):
        # NumPy 1.14, 2018-02-14
        warnings.warn(
            "StructureFormat has been replaced by StructuredVoidFormat",
            DeprecationWarning, stacklevel=2)
        super(StructureFormat, self).__init__(*args, **kwargs)