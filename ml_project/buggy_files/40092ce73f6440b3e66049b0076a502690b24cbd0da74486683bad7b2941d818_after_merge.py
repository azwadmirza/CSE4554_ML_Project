    def compile_specific_catalogs(self, specified_files):
        # type: (List[unicode]) -> None
        def to_domain(fpath):
            # type: (unicode) -> unicode
            docname = self.env.path2doc(path.abspath(fpath))
            if docname:
                return find_catalog(docname, self.config.gettext_compact)
            else:
                return None

        specified_domains = set(map(to_domain, specified_files))
        specified_domains.discard(None)
        catalogs = i18n.find_catalog_source_files(
            [path.join(self.srcdir, x) for x in self.config.locale_dirs],
            self.config.language,
            domains=list(specified_domains),
            charset=self.config.source_encoding,
            excluded=Matcher(['**/.?**']))
        message = __('targets for %d po files that are specified') % len(catalogs)
        self.compile_catalogs(catalogs, message)