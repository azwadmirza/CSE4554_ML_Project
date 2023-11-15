    def provide_context_and_uptodate(self, dirname, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation."""
        kw = {
            "translations": self.site.config['TRANSLATIONS'],
            "filters": self.site.config['FILTERS'],
        }
        context = {
            "title": self.site.config['BLOG_TITLE'](lang),
            "pagekind": ["list", "front_page", "page_index"] if dirname == '' else ["list", "page_index"],
        }
        kw.update(context)
        return context, kw