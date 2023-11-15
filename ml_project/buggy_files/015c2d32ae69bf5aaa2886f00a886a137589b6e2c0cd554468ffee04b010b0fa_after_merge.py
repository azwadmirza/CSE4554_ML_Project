    def postprocess_posts_per_classification(self, posts_per_classification_per_language, flat_hierarchy_per_lang=None, hierarchy_lookup_per_lang=None):
        """Rearrange, modify or otherwise use the list of posts per classification and per language."""
        # Build a lookup table for archive navigation, if we’ll need one.
        if self.site.config['CREATE_ARCHIVE_NAVIGATION']:
            if flat_hierarchy_per_lang is None:
                raise ValueError('Archives need flat_hierarchy_per_lang')
            self.archive_navigation = {}
            for lang, flat_hierarchy in flat_hierarchy_per_lang.items():
                self.archive_navigation[lang] = defaultdict(list)
                for node in flat_hierarchy:
                    if not self.site.config["SHOW_UNTRANSLATED_POSTS"]:
                        if not [x for x in posts_per_classification_per_language[lang][node.classification_name] if x.is_translation_available(lang)]:
                            continue
                    self.archive_navigation[lang][len(node.classification_path)].append(node.classification_name)

                # We need to sort it. Natsort means it’s year 10000 compatible!
                for k, v in self.archive_navigation[lang].items():
                    self.archive_navigation[lang][k] = natsort.natsorted(v, alg=natsort.ns.F | natsort.ns.IC)

        return super(Archive, self).postprocess_posts_per_classification(posts_per_classification_per_language, flat_hierarchy_per_lang, hierarchy_lookup_per_lang)