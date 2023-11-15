    def provide_context_and_uptodate(self, classification, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation."""
        descriptions = self.site.config['AUTHOR_PAGES_DESCRIPTIONS']
        kw = {
            "messages": self.site.MESSAGES,
        }
        context = {
            "author": classification,
            "title": kw["messages"][lang]["Posts by %s"] % classification,
            "description": descriptions[lang][classification] if lang in descriptions and classification in descriptions[lang] else None,
            "pagekind": ["index" if self.show_list_as_index else "list", "author_page"],
        }
        kw.update(context)
        return context, kw