    def compile_specific_catalogs(self, specified_files):
        def to_domain(fpath):
            docname, _ = path.splitext(path_stabilize(fpath))
            dom = find_catalog(docname, self.config.gettext_compact)
            return dom

        specified_domains = set(map(to_domain, specified_files))
        catalogs = i18n.find_catalog_source_files(
            [path.join(self.srcdir, x) for x in self.config.locale_dirs],
            self.config.language,
            domains=list(specified_domains),
            charset=self.config.source_encoding,
            gettext_compact=self.config.gettext_compact)
        message = 'targets for %d po files that are specified' % len(catalogs)
        self.compile_catalogs(catalogs, message)