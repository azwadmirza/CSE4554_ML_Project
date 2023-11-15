    def _generate_classification_page(self, taxonomy, classification, post_list, lang):
        """Render index or post list and associated feeds per classification."""
        # Filter list
        filtered_posts = self._filter_list(post_list, lang)
        if len(filtered_posts) == 0 and taxonomy.omit_empty_classifications:
            return
        # Should we create this list?
        generate_list = taxonomy.should_generate_classification_page(classification, filtered_posts, lang)
        generate_rss = taxonomy.should_generate_rss_for_classification_page(classification, filtered_posts, lang)
        if not generate_list and not generate_rss:
            return
        # Get data
        node = None
        if taxonomy.has_hierarchy:
            node = self.site.hierarchy_lookup_per_classification[taxonomy.classification_name][lang][classification]
        context, kw = taxonomy.provide_context_and_uptodate(classification, lang, node)
        kw = copy(kw)
        kw["messages"] = self.site.MESSAGES
        kw["translations"] = self.site.config['TRANSLATIONS']
        kw["filters"] = self.site.config['FILTERS']
        kw["site_url"] = self.site.config['SITE_URL']
        kw["blog_title"] = self.site.config['BLOG_TITLE']
        kw["generate_rss"] = self.site.config['GENERATE_RSS']
        kw["feed_teasers"] = self.site.config["FEED_TEASERS"]
        kw["feed_plain"] = self.site.config["FEED_PLAIN"]
        kw["feed_links_append_query"] = self.site.config["FEED_LINKS_APPEND_QUERY"]
        kw["feed_length"] = self.site.config['FEED_LENGTH']
        kw["output_folder"] = self.site.config['OUTPUT_FOLDER']
        kw["pretty_urls"] = self.site.config['PRETTY_URLS']
        kw["strip_indexes"] = self.site.config['STRIP_INDEXES']
        kw["index_file"] = self.site.config['INDEX_FILE']
        context = copy(context)
        context["permalink"] = self.site.link(taxonomy.classification_name, classification, lang)
        blinker.signal('generate_classification_page').send({
            'site': self.site,
            'taxonomy': taxonomy,
            'classification': classification,
            'lang': lang,
            'posts': filtered_posts,
            'context': context,
            'kw': kw,
        })
        # Decide what to do
        if taxonomy.has_hierarchy and taxonomy.show_list_as_subcategories_list:
            # Determine whether there are subcategories
            node = self.site.hierarchy_lookup_per_classification[taxonomy.classification_name][lang][classification]
            # Are there subclassifications?
            if len(node.children) > 0:
                # Yes: create list with subclassifications instead of list of posts
                if generate_list:
                    yield self._generate_subclassification_page(taxonomy, node, context, kw, lang)
                return
        # Generate RSS feed
        if generate_rss and kw["generate_rss"] and not taxonomy.always_disable_rss:
            yield self._generate_classification_page_as_rss(taxonomy, classification, filtered_posts, context['title'], context.get("description"), kw, lang)
        # Render HTML
        if generate_list and taxonomy.show_list_as_index:
            yield self._generate_classification_page_as_index(taxonomy, classification, filtered_posts, context, kw, lang)
        elif generate_list:
            yield self._generate_classification_page_as_list(taxonomy, classification, filtered_posts, context, kw, lang)