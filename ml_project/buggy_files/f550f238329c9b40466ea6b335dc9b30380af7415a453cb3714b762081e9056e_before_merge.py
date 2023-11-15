            def create_module(self, spec):
                return importlib.import_module('._distutils', 'setuptools')