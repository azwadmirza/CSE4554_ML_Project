    def merge_upload(self, request, fileobj, overwrite, author=None,
                     merge_header=True, method='translate', fuzzy=''):
        """Top level handler for file uploads."""
        filecopy = fileobj.read()
        fileobj.close()

        # Strip possible UTF-8 BOM
        if filecopy[:3] == codecs.BOM_UTF8:
            filecopy = filecopy[3:]

        # Load backend file
        store = try_load(
            fileobj.name,
            filecopy,
            self.subproject.file_format_cls,
            self.subproject.template_store
        )

        # Optionally set authorship
        if author is None:
            author = get_author_name(request.user)

        # Check valid plural forms
        if hasattr(store.store, 'parseheader'):
            header = store.store.parseheader()
            if 'Plural-Forms' in header and \
                    not self.language.same_plural(header['Plural-Forms']):
                raise Exception('Plural forms do not match the language.')

        if method in ('translate', 'fuzzy'):
            # Merge on units level
            with self.subproject.repository.lock:
                return self.merge_translations(
                    request,
                    store,
                    overwrite,
                    (method == 'fuzzy'),
                    fuzzy,
                    merge_header,
                )

        # Add as sugestions
        return self.merge_suggestions(request, store, fuzzy)