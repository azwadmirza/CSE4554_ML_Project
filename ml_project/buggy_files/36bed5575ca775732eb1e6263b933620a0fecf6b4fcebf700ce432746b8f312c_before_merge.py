    def __init__(self, *args, **kwargs):
        super(SpyderKernel, self).__init__(*args, **kwargs)

        self.namespace_view_settings = {}
        self._pdb_obj = None
        self._pdb_step = None