    def postprocess_posts_per_classification(self, posts_per_classification_per_language, flat_hierarchy_per_lang=None, hierarchy_lookup_per_lang=None):
        """Rearrange, modify or otherwise use the list of posts per classification and per language."""
        more_than_one = False
        for lang, posts_per_author in posts_per_classification_per_language.items():
            authors = set()
            for author, posts in posts_per_author.items():
                for post in posts:
                    if not self.site.config["SHOW_UNTRANSLATED_POSTS"] and not post.is_translation_available(lang):
                        continue
                    authors.add(author)
            if len(authors) > 1:
                more_than_one = True
        self.generate_author_pages = self.site.config["ENABLE_AUTHOR_PAGES"] and more_than_one
        self.site.GLOBAL_CONTEXT["author_pages_generated"] = self.generate_author_pages
        self.translation_manager.add_defaults(posts_per_classification_per_language)