        def find_spec(self, fullname, path, target=None):
            if fullname in _DISTUTILS_PATCH and self.fullname is None:
                with self.lock:
                    self.fullname = fullname
                    try:
                        spec = find_spec(fullname, path)
                        if spec is not None:
                            old = spec.loader.exec_module

                            def exec_module(module):
                                old(module)
                                patch_dist(module)

                            spec.loader.exec_module = exec_module
                            return spec
                    finally:
                        self.fullname = None