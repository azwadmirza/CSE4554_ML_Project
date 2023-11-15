    def __init__(self, storefile, template_store=None, language_code=None):
        """Create file format object, wrapping up translate-toolkit's store."""
        self.storefile = storefile
        # Load store
        if isinstance(storefile, TranslationStore):
            # Used by XLSX writer
            self.store = storefile
        else:
            self.store = self.load(storefile)
        # Check store validity
        if not self.is_valid(self.store):
            raise ValueError(
                'Invalid file format {0}'.format(repr(self.store))
            )
        # Remember template
        self.template_store = template_store
        # Set language (needed for some which do not include this)
        if (language_code is not None and
                self.store.gettargetlanguage() is None):
            self.store.settargetlanguage(language_code)