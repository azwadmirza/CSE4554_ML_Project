    def _do_classification(self, site):
        # Needed to avoid strange errors during tests
        if site is not self.site:
            return

        # Get list of enabled taxonomy plugins and initialize data structures
        taxonomies = site.taxonomy_plugins.values()
        site.posts_per_classification = {}
        for taxonomy in taxonomies:
            site.posts_per_classification[taxonomy.classification_name] = {
                lang: defaultdict(set) for lang in site.config['TRANSLATIONS'].keys()
            }

        # Classify posts
        for post in site.timeline:
            # Do classify pages, but don’t classify posts that are hidden
            # (draft/private/future)
            if post.is_post and not post.use_in_feeds:
                continue
            for taxonomy in taxonomies:
                if taxonomy.apply_to_posts if post.is_post else taxonomy.apply_to_pages:
                    classifications = {}
                    for lang in site.config['TRANSLATIONS'].keys():
                        # Extract classifications for this language
                        classifications[lang] = taxonomy.classify(post, lang)
                        if not taxonomy.more_than_one_classifications_per_post and len(classifications[lang]) > 1:
                            raise ValueError("Too many {0} classifications for post {1}".format(taxonomy.classification_name, post.source_path))
                        # Add post to sets
                        for classification in classifications[lang]:
                            while True:
                                site.posts_per_classification[taxonomy.classification_name][lang][classification].add(post)
                                if not taxonomy.include_posts_from_subhierarchies or not taxonomy.has_hierarchy:
                                    break
                                classification_path = taxonomy.extract_hierarchy(classification)
                                if len(classification_path) <= 1:
                                    if len(classification_path) == 0 or not taxonomy.include_posts_into_hierarchy_root:
                                        break
                                classification = taxonomy.recombine_classification_from_hierarchy(classification_path[:-1])

        # Sort everything.
        site.page_count_per_classification = {}
        site.hierarchy_per_classification = {}
        site.flat_hierarchy_per_classification = {}
        site.hierarchy_lookup_per_classification = {}
        for taxonomy in taxonomies:
            site.page_count_per_classification[taxonomy.classification_name] = {}
            # Sort post lists
            for lang, posts_per_classification in site.posts_per_classification[taxonomy.classification_name].items():
                # Ensure implicit classifications are inserted
                for classification in taxonomy.get_implicit_classifications(lang):
                    if classification not in posts_per_classification:
                        posts_per_classification[classification] = []
                site.page_count_per_classification[taxonomy.classification_name][lang] = {}
                # Convert sets to lists and sort them
                for classification in list(posts_per_classification.keys()):
                    posts = list(posts_per_classification[classification])
                    posts = self.site.sort_posts_chronologically(posts, lang)
                    taxonomy.sort_posts(posts, classification, lang)
                    posts_per_classification[classification] = posts
            # Create hierarchy information
            if taxonomy.has_hierarchy:
                site.hierarchy_per_classification[taxonomy.classification_name] = {}
                site.flat_hierarchy_per_classification[taxonomy.classification_name] = {}
                site.hierarchy_lookup_per_classification[taxonomy.classification_name] = {}
                for lang, posts_per_classification in site.posts_per_classification[taxonomy.classification_name].items():
                    # Compose hierarchy
                    hierarchy = {}
                    for classification in posts_per_classification.keys():
                        hier = taxonomy.extract_hierarchy(classification)
                        node = hierarchy
                        for he in hier:
                            if he not in node:
                                node[he] = {}
                            node = node[he]
                    hierarchy_lookup = {}

                    def create_hierarchy(hierarchy, parent=None, level=0):
                        """Create hierarchy."""
                        result = {}
                        for name, children in hierarchy.items():
                            node = hierarchy_utils.TreeNode(name, parent)
                            node.children = create_hierarchy(children, node, level + 1)
                            node.classification_path = [pn.name for pn in node.get_path()]
                            node.classification_name = taxonomy.recombine_classification_from_hierarchy(node.classification_path)
                            hierarchy_lookup[node.classification_name] = node
                            result[node.name] = node
                        classifications = natsort.natsorted(result.keys(), alg=natsort.ns.F | natsort.ns.IC)
                        taxonomy.sort_classifications(classifications, lang, level=level)
                        return [result[classification] for classification in classifications]

                    root_list = create_hierarchy(hierarchy)
                    if '' in posts_per_classification:
                        node = hierarchy_utils.TreeNode('', parent=None)
                        node.children = root_list
                        node.classification_path = []
                        node.classification_name = ''
                        hierarchy_lookup[node.name] = node
                        root_list = [node]
                    flat_hierarchy = hierarchy_utils.flatten_tree_structure(root_list)
                    # Store result
                    site.hierarchy_per_classification[taxonomy.classification_name][lang] = root_list
                    site.flat_hierarchy_per_classification[taxonomy.classification_name][lang] = flat_hierarchy
                    site.hierarchy_lookup_per_classification[taxonomy.classification_name][lang] = hierarchy_lookup
                taxonomy.postprocess_posts_per_classification(site.posts_per_classification[taxonomy.classification_name],
                                                              site.flat_hierarchy_per_classification[taxonomy.classification_name],
                                                              site.hierarchy_lookup_per_classification[taxonomy.classification_name])
            else:
                taxonomy.postprocess_posts_per_classification(site.posts_per_classification[taxonomy.classification_name])

        # Check for valid paths and for collisions
        taxonomy_outputs = {lang: dict() for lang in site.config['TRANSLATIONS'].keys()}
        quit = False
        for taxonomy in taxonomies:
            # Check for collisions (per language)
            for lang in site.config['TRANSLATIONS'].keys():
                if not taxonomy.is_enabled(lang):
                    continue
                for tlang in site.config['TRANSLATIONS'].keys():
                    if lang != tlang and not taxonomy.also_create_classifications_from_other_languages:
                        continue
                    for classification, posts in site.posts_per_classification[taxonomy.classification_name][tlang].items():
                        # Obtain path as tuple
                        path = site.path_handlers[taxonomy.classification_name](classification, lang)
                        # Check that path is OK
                        for path_element in path:
                            if len(path_element) == 0:
                                utils.LOGGER.error("{0} {1} yields invalid path '{2}'!".format(taxonomy.classification_name.title(), classification, '/'.join(path)))
                                quit = True
                        # Combine path
                        path = os.path.join(*[os.path.normpath(p) for p in path if p != '.'])
                        # Determine collisions
                        if path in taxonomy_outputs[lang]:
                            other_classification_name, other_classification, other_posts = taxonomy_outputs[lang][path]
                            if other_classification_name == taxonomy.classification_name and other_classification == classification:
                                taxonomy_outputs[lang][path][2].extend(posts)
                            else:
                                utils.LOGGER.error('You have classifications that are too similar: {0} "{1}" and {2} "{3}" both result in output path {4} for language {5}.'.format(
                                    taxonomy.classification_name, classification, other_classification_name, other_classification, path, lang))
                                utils.LOGGER.error('{0} {1} is used in: {2}'.format(
                                    taxonomy.classification_name.title(), classification, ', '.join(sorted([p.source_path for p in posts]))))
                                utils.LOGGER.error('{0} {1} is used in: {2}'.format(
                                    other_classification_name.title(), other_classification, ', '.join(sorted([p.source_path for p in other_posts]))))
                                quit = True
                        else:
                            taxonomy_outputs[lang][path] = (taxonomy.classification_name, classification, list(posts))
        if quit:
            sys.exit(1)
        blinker.signal('taxonomies_classified').send(site)