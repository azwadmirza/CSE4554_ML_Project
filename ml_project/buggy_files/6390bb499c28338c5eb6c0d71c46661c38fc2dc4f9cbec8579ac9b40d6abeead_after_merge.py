    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super(ClassifyCategories, self).set_site(site)
        self.show_list_as_index = self.site.config['CATEGORY_PAGES_ARE_INDEXES']
        self.template_for_single_list = "tagindex.tmpl" if self.show_list_as_index else "tag.tmpl"
        self.translation_manager = utils.ClassificationTranslationManager()