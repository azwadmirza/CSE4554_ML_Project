        def find_spec(self, fullname, path, target=None):
            if fullname in _DISTUTILS_PATCH and self.fullname is None:
                with self.lock:
                    self.fullname = fullname
                    try:
                        spec = find_spec(fullname, path)
                        if spec is not None:
                            # https://www.python.org/dev/peps/pep-0451/#how-loading-will-work
                            is_new_api = hasattr(spec.loader, "exec_module")
                            func_name = "exec_module" if is_new_api else "load_module"
                            old = getattr(spec.loader, func_name)
                            func = self.exec_module if is_new_api else self.load_module
                            if old is not func:
                                try:
                                    setattr(spec.loader, func_name, partial(func, old))
                                except AttributeError:
                                    pass  # C-Extension loaders are r/o such as zipimporter with <python 3.7
                            return spec
                    finally:
                        self.fullname = None