    def get_path(self, author, lang, dest_type='page'):
        """Return a path for the given classification."""
        if self.site.config['SLUG_AUTHOR_PATH']:
            slug = utils.slugify(author, lang)
        else:
            slug = author
        return [self.site.config['AUTHOR_PATH'](lang), slug], 'auto'