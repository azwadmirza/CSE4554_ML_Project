    def postprocess_posts_per_classification(self, posts_per_classification_per_language, flat_hierarchy_per_lang=None, hierarchy_lookup_per_lang=None):
        """Rearrange, modify or otherwise use the list of posts per classification and per language."""
        for lang, posts_per_section in posts_per_classification_per_language.items():
            # Don't build sections when there is only one, a.k.a. default setups
            sections = set()
            for section, posts in posts_per_section.items():
                for post in posts:
                    if not self.site.config["SHOW_UNTRANSLATED_POSTS"] and not post.is_translation_available(lang):
                        continue
                    sections.add(section)
            self.enable_for_lang[lang] = (len(sections) > 1)
        self.translation_manager.read_from_config(self.site, 'POSTS_SECTION', posts_per_classification_per_language, False)