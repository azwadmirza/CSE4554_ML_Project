    def get_path(self, classification, lang, dest_type='page'):
        """Return a path for the given classification."""
        if self.site.config['SLUG_AUTHOR_PATH']:
            slug = utils.slugify(classification, lang)
        else:
            slug = classification
        return [self.site.config['AUTHOR_PATH'](lang), slug], 'auto'