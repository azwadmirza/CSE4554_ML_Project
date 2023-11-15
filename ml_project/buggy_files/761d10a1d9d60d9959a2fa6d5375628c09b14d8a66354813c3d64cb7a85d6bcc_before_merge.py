    def compile_all_catalogs(self):
        catalogs = i18n.find_catalog_source_files(
            [path.join(self.srcdir, x) for x in self.config.locale_dirs],
            self.config.language,
            gettext_compact=self.config.gettext_compact,
            force_all=True)
        message = 'all of %d po files' % len(catalogs)
        self.compile_catalogs(catalogs, message)