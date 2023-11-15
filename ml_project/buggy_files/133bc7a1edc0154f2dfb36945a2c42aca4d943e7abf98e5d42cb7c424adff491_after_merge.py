    def set_site(self, site):
        """Set Nikola site."""
        super(ClassifyAuthors, self).set_site(site)
        self.show_list_as_index = site.config['AUTHOR_PAGES_ARE_INDEXES']
        self.template_for_single_list = "authorindex.tmpl" if self.show_list_as_index else "author.tmpl"
        self.translation_manager = utils.ClassificationTranslationManager()