    def _prepare(self, channel):
        """Prepare context and category hierarchy."""
        self.context = self.populate_context(channel)
        self.base_dir = urlparse(self.context['BASE_URL']).path

        if self.export_categories_as_categories:
            wordpress_namespace = channel.nsmap['wp']
            cat_map = dict()
            for cat in channel.findall('{{{0}}}category'.format(wordpress_namespace)):
                # cat_id = get_text_tag(cat, '{{{0}}}term_id'.format(wordpress_namespace), None)
                cat_slug = get_text_tag(cat, '{{{0}}}category_nicename'.format(wordpress_namespace), None)
                cat_parent_slug = get_text_tag(cat, '{{{0}}}category_parent'.format(wordpress_namespace), None)
                cat_name = utils.html_unescape(get_text_tag(cat, '{{{0}}}cat_name'.format(wordpress_namespace), None))
                cat_path = [cat_name]
                if cat_parent_slug in cat_map:
                    cat_path = cat_map[cat_parent_slug] + cat_path
                cat_map[cat_slug] = cat_path
            self._category_paths = dict()
            for cat, path in cat_map.items():
                self._category_paths[cat] = utils.join_hierarchical_category_path(path)