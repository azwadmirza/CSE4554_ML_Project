    def compile_catalogs(self, catalogs, message):
        # type: (Set[CatalogInfo], unicode) -> None
        if not self.config.gettext_auto_build:
            return

        def cat2relpath(cat):
            # type: (CatalogInfo) -> unicode
            return path.relpath(cat.mo_path, self.env.srcdir).replace(path.sep, SEP)

        logger.info(bold('building [mo]: ') + message)
        for catalog in status_iterator(catalogs, 'writing output... ', "darkgreen",
                                       len(catalogs), self.app.verbosity,
                                       stringify_func=cat2relpath):
            catalog.write_mo(self.config.language)