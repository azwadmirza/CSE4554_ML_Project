    def add_latex_package(self, packagename, options=None):
        self.debug('[app] adding latex package: %r', packagename)
        if hasattr(self.builder, 'usepackages'):  # only for LaTeX builder
            self.builder.usepackages.append((packagename, options))