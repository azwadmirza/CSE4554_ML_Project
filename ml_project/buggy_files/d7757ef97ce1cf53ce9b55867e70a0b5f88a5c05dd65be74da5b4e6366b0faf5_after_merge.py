    def _generate_classification_page(self, taxonomy, classification, filtered_posts, generate_list, generate_rss, lang, post_lists_per_lang, classification_set_per_lang=None):
        """Render index or post list and associated feeds per classification."""
        # Should we create this list?
        if not generate_list and not generate_rss:
            return
        # Get data
        node = None
        if taxonomy.has_hierarchy:
            node = self.site.hierarchy_lookup_per_classification[taxonomy.classification_name][lang].get(classification)
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
        context["kind"] = taxonomy.classification_name
        # Get links to other language versions of this classification
        if classification_set_per_lang is not None:
            other_lang_links = taxonomy.get_other_language_variants(classification, lang, classification_set_per_lang)
            # Collect by language
            links_per_lang = defaultdict(list)
            for other_lang, link in other_lang_links:
                # Make sure we ignore the current language (in case the
                # plugin accidentally returns links for it as well)
                if other_lang != lang:
                    links_per_lang[other_lang].append(link)
            # Sort first by language, then by classification
            sorted_links = []
            sorted_links_all = []
            for other_lang in sorted(list(links_per_lang.keys()) + [lang]):
                if other_lang == lang:
                    sorted_links_all.append((lang, classification, taxonomy.get_classification_friendly_name(classification, lang)))
                else:
                    links = hierarchy_utils.sort_classifications(taxonomy, links_per_lang[other_lang], other_lang)
                    links = [(other_lang, other_classification,
                              taxonomy.get_classification_friendly_name(other_classification, other_lang))
                             for other_classification in links if post_lists_per_lang[other_lang].get(other_classification, ('', False, False))[1]]
                    sorted_links.extend(links)
                    sorted_links_all.extend(links)
            # Store result in context and kw
            context['has_other_languages'] = True
            context['other_languages'] = sorted_links
            context['all_languages'] = sorted_links_all
            kw['other_languages'] = sorted_links
            kw['all_languages'] = sorted_links_all
        else:
            context['has_other_languages'] = False
        # Allow other plugins to modify the result
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