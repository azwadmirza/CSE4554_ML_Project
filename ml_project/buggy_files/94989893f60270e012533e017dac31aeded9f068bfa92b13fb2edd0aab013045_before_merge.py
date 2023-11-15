    def slugify_category_name(self, path, lang):
        """Slugify a category name."""
        if lang is None:  # TODO: remove in v8
            utils.LOGGER.warn("ClassifyCategories.slugify_category_name() called without language!")
            lang = ''
        if self.site.config['CATEGORY_OUTPUT_FLAT_HIERARCHY']:
            path = path[-1:]  # only the leaf
        result = [self.slugify_tag_name(part, lang) for part in path]
        result[0] = self.site.config['CATEGORY_PREFIX'] + result[0]
        if not self.site.config['PRETTY_URLS']:
            result = ['-'.join(result)]
        return result