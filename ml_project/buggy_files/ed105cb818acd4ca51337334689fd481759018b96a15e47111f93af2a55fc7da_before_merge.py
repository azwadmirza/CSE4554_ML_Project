    def provide_context_and_uptodate(self, classification, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation."""
        kw = {
            "tag_path": self.site.config['TAG_PATH'],
            "tag_pages_are_indexes": self.site.config['TAG_PAGES_ARE_INDEXES'],
            "taglist_minimum_post_count": self.site.config['TAGLIST_MINIMUM_POSTS'],
            "tzinfo": self.site.tzinfo,
            "tag_pages_descriptions": self.site.config['TAG_PAGES_DESCRIPTIONS'],
            "tag_pages_titles": self.site.config['TAG_PAGES_TITLES'],
        }
        context = {
            "title": self.site.config['TAG_PAGES_TITLES'].get(lang, {}).get(classification, self.site.MESSAGES[lang]["Posts about %s"] % classification),
            "description": self.site.config['TAG_PAGES_DESCRIPTIONS'].get(lang, {}).get(classification),
            "pagekind": ["tag_page", "index" if self.show_list_as_index else "list"],
            "tag": classification,
        }
        if self.show_list_as_index:
            context["rss_link"] = """<link rel="alternate" type="application/rss+xml" type="application/rss+xml" title="RSS for tag {0} ({1})" href="{2}">""".format(classification, lang, self.site.link("tag_rss", classification, lang))
        kw.update(context)
        return context, kw