    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super(ClassifyTags, self).set_site(site)
        self.show_list_as_index = self.site.config['TAG_PAGES_ARE_INDEXES']
        self.template_for_single_list = "tagindex.tmpl" if self.show_list_as_index else "tag.tmpl"
        self.minimum_post_count_per_classification_in_overview = self.site.config['TAGLIST_MINIMUM_POSTS']
        self.translation_manager = utils.ClassificationTranslationManager()