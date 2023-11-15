    def spec_for_distutils(self):
        import importlib.abc
        import importlib.util

        class DistutilsLoader(importlib.abc.Loader):

            def create_module(self, spec):
                return importlib.import_module('setuptools._distutils')

            def exec_module(self, module):
                pass

        return importlib.util.spec_from_loader('distutils', DistutilsLoader())