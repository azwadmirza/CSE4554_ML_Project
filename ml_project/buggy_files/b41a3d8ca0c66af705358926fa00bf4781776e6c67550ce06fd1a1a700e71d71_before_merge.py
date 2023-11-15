    def gen_tasks(self):
        """Render the tag pages and feeds."""
        self.site.scan_posts()
        yield self.group_task()

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

                # Generate classification lists
                classifications = {}
                for tlang, posts_per_classification in self.site.posts_per_classification[taxonomy.classification_name].items():
                    if lang != tlang and not taxonomy.also_create_classifications_from_other_languages:
                        continue
                    classifications.update(posts_per_classification)

                # Process classifications
                for classification, posts in classifications.items():
                    for task in self._generate_classification_page(taxonomy, classification, posts, lang):
                        yield task
            # In case we are ignoring plugins for overview, we must have a collision for
            # tags and categories. Handle this special case with extra code.
            if ignore_plugins_for_overview:
                for task in self._generate_tag_and_category_overview(self.site.taxonomy_plugins['tag'], self.site.taxonomy_plugins['category'], lang):
                    yield task