    def _generate_classification_overview_kw_context(self, taxonomy, lang):
        """Create context and kw for a classification overview page."""
        context, kw = taxonomy.provide_overview_context_and_uptodate(lang)

        context = copy(context)
        kw = copy(kw)
        kw["messages"] = self.site.MESSAGES
        kw["translations"] = self.site.config['TRANSLATIONS']
        kw["filters"] = self.site.config['FILTERS']
        kw["minimum_post_count"] = taxonomy.minimum_post_count_per_classification_in_overview
        kw["output_folder"] = self.site.config['OUTPUT_FOLDER']
        kw["pretty_urls"] = self.site.config['PRETTY_URLS']
        kw["strip_indexes"] = self.site.config['STRIP_INDEXES']
        kw["index_file"] = self.site.config['INDEX_FILE']

        # Collect all relevant classifications
        if taxonomy.has_hierarchy:
            def acceptor(node):
                return len(self._filter_list(self.site.posts_per_classification[taxonomy.classification_name][lang][node.classification_name], lang)) >= kw["minimum_post_count"]

            clipped_root_list = [hierarchy_utils.clone_treenode(node, parent=None, acceptor=acceptor) for node in self.site.hierarchy_per_classification[taxonomy.classification_name][lang]]
            clipped_root_list = [node for node in clipped_root_list if node]
            clipped_flat_hierarchy = hierarchy_utils.flatten_tree_structure(clipped_root_list)

            classifications = [cat.classification_name for cat in clipped_flat_hierarchy]
        else:
            classifications = natsort.natsorted([tag for tag, posts in self.site.posts_per_classification[taxonomy.classification_name][lang].items()
                                                 if len(self._filter_list(posts, lang)) >= kw["minimum_post_count"]],
                                                alg=natsort.ns.F | natsort.ns.IC)
            taxonomy.sort_classifications(classifications, lang)

        # Set up classifications in context
        context[taxonomy.overview_page_variable_name] = classifications
        context["has_hierarchy"] = taxonomy.has_hierarchy
        if taxonomy.overview_page_items_variable_name:
            items = [(classification,
                      self.site.link(taxonomy.classification_name, classification, lang))
                     for classification in classifications]
            items_with_postcount = [
                (classification,
                 self.site.link(taxonomy.classification_name, classification, lang),
                 len(self._filter_list(self.site.posts_per_classification[taxonomy.classification_name][lang][classification], lang)))
                for classification in classifications
            ]
            context[taxonomy.overview_page_items_variable_name] = items
            context[taxonomy.overview_page_items_variable_name + "_with_postcount"] = items_with_postcount
        if taxonomy.has_hierarchy and taxonomy.overview_page_hierarchy_variable_name:
            hier_items = [
                (node.name, node.classification_name, node.classification_path,
                 self.site.link(taxonomy.classification_name, node.classification_name, lang),
                 node.indent_levels, node.indent_change_before,
                 node.indent_change_after)
                for node in clipped_flat_hierarchy
            ]
            hier_items_with_postcount = [
                (node.name, node.classification_name, node.classification_path,
                 self.site.link(taxonomy.classification_name, node.classification_name, lang),
                 node.indent_levels, node.indent_change_before,
                 node.indent_change_after,
                 len(node.children),
                 len(self._filter_list(self.site.posts_per_classification[taxonomy.classification_name][lang][node.classification_name], lang)))
                for node in clipped_flat_hierarchy
            ]
            context[taxonomy.overview_page_hierarchy_variable_name] = hier_items
            context[taxonomy.overview_page_hierarchy_variable_name + '_with_postcount'] = hier_items_with_postcount
        return context, kw