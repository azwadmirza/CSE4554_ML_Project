    def _create_metadata(self, status, excerpt, tags, categories, post_name=None):
        """Create post metadata."""
        other_meta = {'wp-status': status}
        if excerpt is not None:
            other_meta['excerpt'] = excerpt
        if self.export_categories_as_categories:
            cats = []
            for text in categories:
                if text in self._category_paths:
                    cats.append(self._category_paths[text])
                else:
                    cats.append(hierarchy_utils.join_hierarchical_category_path([utils.html_unescape(text)]))
            other_meta['categories'] = ','.join(cats)
            if len(cats) > 0:
                other_meta['category'] = cats[0]
                if len(cats) > 1:
                    LOGGER.warn(('Post "{0}" has more than one category! ' +
                                 'Will only use the first one.').format(post_name))
            tags_cats = [utils.html_unescape(tag) for tag in tags]
        else:
            tags_cats = [utils.html_unescape(tag) for tag in tags + categories]
        return tags_cats, other_meta