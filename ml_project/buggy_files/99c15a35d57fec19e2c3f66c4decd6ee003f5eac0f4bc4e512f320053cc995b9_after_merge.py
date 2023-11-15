    def provide_context_and_uptodate(self, classification, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation."""
        kw = {
            "messages": self.site.MESSAGES,
        }
        section_name = self._get_section_name(classification, lang)
        # Compose section title
        section_title = section_name
        posts_section_title = self.site.config['POSTS_SECTION_TITLE'](lang)
        if isinstance(posts_section_title, dict):
            if classification in posts_section_title:
                section_title = posts_section_title[classification]
        elif isinstance(posts_section_title, (utils.bytes_str, utils.unicode_str)):
            section_title = posts_section_title
        section_title = section_title.format(name=section_name)
        # Compose context
        context = {
            "title": section_title,
            "description": self.site.config['POSTS_SECTION_DESCRIPTIONS'](lang)[classification] if classification in self.site.config['POSTS_SECTION_DESCRIPTIONS'](lang) else "",
            "pagekind": ["section_page", "index" if self.show_list_as_index else "list"],
            "section": classification,
        }
        kw.update(context)
        return context, kw