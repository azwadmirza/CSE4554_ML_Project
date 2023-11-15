    def gen_tasks(self):
        """Render the tag pages and feeds."""
        self.site.scan_posts()
        yield self.group_task()

        # Cache classification sets per language for taxonomies where
        # add_other_languages_variable is True.
        classification_set_per_lang = {}
        for taxonomy in self.site.taxonomy_plugins.values():
            if taxonomy.add_other_languages_variable:
                lookup = self.site.posts_per_classification[taxonomy.classification_name]
                cspl = {lang: set(lookup[lang].keys()) for lang in lookup}
                classification_set_per_lang[taxonomy.classification_name] = cspl

        # Collect post lists for classification pages and determine whether
        # they should be generated.
        post_lists_per_lang = {}
        for taxonomy in self.site.taxonomy_plugins.values():
            plpl = {}
            for lang in self.site.config["TRANSLATIONS"]:
                classifications = {}
                for tlang, posts_per_classification in self.site.posts_per_classification[taxonomy.classification_name].items():
                    if lang != tlang and not taxonomy.also_create_classifications_from_other_languages:
                        continue
                    classifications.update(posts_per_classification)
                result = {}
                for classification, posts in classifications.items():
                    # Filter list
                    filtered_posts = self._filter_list(posts, lang)
                    if len(filtered_posts) == 0 and taxonomy.omit_empty_classifications:
                        generate_list = False
                        generate_rss = False
                    else:
                        # Should we create this list?
                        generate_list = taxonomy.should_generate_classification_page(classification, filtered_posts, lang)
                        generate_rss = taxonomy.should_generate_rss_for_classification_page(classification, filtered_posts, lang)
                    result[classification] = (filtered_posts, generate_list, generate_rss)
                plpl[lang] = result
            post_lists_per_lang[taxonomy.classification_name] = plpl

        # Now generate pages
        for lang in self.site.config["TRANSLATIONS"]:
            # To support that tag and category classifications share the same overview,
            # we explicitly detect this case:
            ignore_plugins_for_overview = set()
            if 'tag' in self.site.taxonomy_plugins and 'category' in self.site.taxonomy_plugins and self.site.link("tag_index", None, lang) == self.site.link("category_index", None, lang):
                # Block both plugins from creating overviews
                ignore_plugins_for_overview.add(self.site.taxonomy_plugins['tag'])
                ignore_plugins_for_overview.add(self.site.taxonomy_plugins['category'])
            for taxonomy in self.site.taxonomy_plugins.values():
                if not taxonomy.is_enabled(lang):
                    continue
                # Generate list of classifications (i.e. classification overview)
                if taxonomy not in ignore_plugins_for_overview:
                    if taxonomy.template_for_classification_overview is not None:
                        for task in self._generate_classification_overview(taxonomy, lang):
                            yield task

                # Process classifications
                for classification, (filtered_posts, generate_list, generate_rss) in post_lists_per_lang[taxonomy.classification_name][lang].items():
                    for task in self._generate_classification_page(taxonomy, classification, filtered_posts,
                                                                   generate_list, generate_rss, lang,
                                                                   post_lists_per_lang[taxonomy.classification_name],
                                                                   classification_set_per_lang.get(taxonomy.classification_name)):
                        yield task
            # In case we are ignoring plugins for overview, we must have a collision for
            # tags and categories. Handle this special case with extra code.
            if ignore_plugins_for_overview:
                for task in self._generate_tag_and_category_overview(self.site.taxonomy_plugins['tag'], self.site.taxonomy_plugins['category'], lang):
                    yield task