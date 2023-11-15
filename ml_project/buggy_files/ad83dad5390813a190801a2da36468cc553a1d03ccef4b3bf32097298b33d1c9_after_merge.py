        def __getattr__(self, item):
            if item.startswith('_pytest') or item in ('__bases__', '__test__'):
                raise AttributeError(item)

            real_mod = importlib.import_module(name, package=package)
            if globals is not None and rename in globals:
                globals[rename] = real_mod
            elif locals is not None:
                locals[rename] = real_mod
            return getattr(real_mod, item)