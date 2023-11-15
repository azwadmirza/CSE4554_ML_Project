    def set_site(self, site):
        """Set Nikola site."""
        self.show_list_as_index = site.config["POSTS_SECTIONS_ARE_INDEXES"]
        self.template_for_single_list = "sectionindex.tmpl" if self.show_list_as_index else "list.tmpl"
        self.enable_for_lang = {}
        return super(ClassifySections, self).set_site(site)