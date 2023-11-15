    def _base_setup_args(self, req):
        return [
            sys.executable, "-u", '-c',
            "import setuptools;__file__=%r;"
            "exec(compile(open(__file__).read().replace('\\r\\n', '\\n'), "
            "__file__, 'exec'))" % req.setup_py
        ] + list(self.global_options)