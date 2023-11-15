    def provide_context_and_uptodate(self, author, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation."""
        descriptions = self.site.config['AUTHOR_PAGES_DESCRIPTIONS']
        kw = {
            "messages": self.site.MESSAGES,
        }
        context = {
            "author": author,
            "title": kw["messages"][lang]["Posts by %s"] % author,
            "description": descriptions[lang][author] if lang in descriptions and author in descriptions[lang] else None,
            "pagekind": ["index" if self.show_list_as_index else "list", "author_page"],
        }
        if self.site.config["GENERATE_RSS"]:
            rss_link = ("""<link rel="alternate" type="application/rss+xml" title="RSS for author {0} ({1})" href="{2}">""".format(
                author, lang, self.site.link('author_rss', author, lang)))
            context['rss_link'] = rss_link
        kw.update(context)
        return context, kw