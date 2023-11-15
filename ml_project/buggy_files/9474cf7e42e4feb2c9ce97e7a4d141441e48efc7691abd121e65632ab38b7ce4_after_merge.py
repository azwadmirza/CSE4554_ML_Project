    def _base_setup_args(self, req):
        return [
            sys.executable, "-u", '-c',
            SETUPTOOLS_SHIM % req.setup_py
        ] + list(self.global_options)