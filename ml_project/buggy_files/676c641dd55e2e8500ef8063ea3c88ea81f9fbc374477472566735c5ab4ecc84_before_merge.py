    def compile_catalogs(self, catalogs, message):
        if not self.config.gettext_auto_build:
            return

        def cat2relpath(cat):
            return path.relpath(cat.mo_path, self.env.srcdir).replace(path.sep, SEP)

        self.info(bold('building [mo]: ') + message)
        for catalog in self.app.status_iterator(
                catalogs, 'writing output... ', darkgreen, len(catalogs),
                cat2relpath):
            catalog.write_mo(self.config.language)