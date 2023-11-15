        def find_spec(self, fullname, path, target=None):
            if fullname in _DISTUTILS_PATCH and self.fullname is None:
                with self.lock:
                    self.fullname = fullname
                    try:
                        spec = find_spec(fullname, path)
                        if spec is not None:
                            # https://www.python.org/dev/peps/pep-0451/#how-loading-will-work
                            spec.loader = deepcopy(spec.loader)  # loaders may be shared, create new that also patches
                            func_name = "exec_module" if hasattr(spec.loader, "exec_module") else "load_module"
                            if func_name == "exec_module":  # new API

                                def patch_module_load(module):
                                    old(module)
                                    patch_dist(module)

                            else:  # legacy API

                                def patch_module_load(name):
                                    module = old(name)
                                    patch_dist(module)
                                    return module

                            old = getattr(spec.loader, func_name)
                            setattr(spec.loader, func_name, patch_module_load)
                            return spec
                    finally:
                        self.fullname = None