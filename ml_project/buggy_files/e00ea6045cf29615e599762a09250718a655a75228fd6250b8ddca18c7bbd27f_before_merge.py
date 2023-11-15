    def should_generate_classification_page(self, dirname, post_list, lang):
        """Only generates list of posts for classification if this function returns True."""
        short_destination = dirname + '/' + self.site.config['INDEX_FILE']
        # If there is an index.html pending to be created from a page, do not generate the section page.
        # The section page would be useless anyways. (via Issue #2613)
        for post in self.site.timeline:
            if not self.site.config["SHOW_UNTRANSLATED_POSTS"] and not post.is_translation_available(lang):
                continue
            if post.destination_path(lang, sep='/') == short_destination:
                return False
        return True