    def compile_all_catalogs(self):
        # type: () -> None
        catalogs = i18n.find_catalog_source_files(
            [path.join(self.srcdir, x) for x in self.config.locale_dirs],
            self.config.language,
            charset=self.config.source_encoding,
            gettext_compact=self.config.gettext_compact,
            force_all=True,
            excluded=Matcher(['**/.?**']))
        message = __('all of %d po files') % len(catalogs)
        self.compile_catalogs(catalogs, message)