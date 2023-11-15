    def __init__(self, *args, **kwargs):
        super(SpyderKernel, self).__init__(*args, **kwargs)

        self.namespace_view_settings = {}

        self._pdb_obj = None
        self._pdb_step = None
        self._do_publish_pdb_state = True
        self._mpl_backend_error = None

        kernel_config = self.config.get('IPKernelApp', None)
        if kernel_config is not None:
            cf = kernel_config['connection_file']
            json_file = osp.basename(cf)
            self._kernel_id = json_file.split('.json')[0]
        else:
            self._kernel_id = None