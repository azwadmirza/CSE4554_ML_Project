    def add_latex_package(self, packagename, options=None):
        self.debug('[app] adding latex package: %r', packagename)
        self.builder.usepackages.append((packagename, options))